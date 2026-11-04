# Copyright 2026 Tecnativa - Víctor Martínez
# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest import mock

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

_MODULE = "odoo.addons.currency_rate_update_frankfurter.models"
_REQUESTS_GET = f"{_MODULE}.res_currency_rate_provider.requests.get"

CURRENCIES_PAYLOAD = [
    {"iso_code": "JOD", "name": "Jordanian Dinar"},
    {"iso_code": "MAD", "name": "Moroccan Dirham"},
    {"iso_code": "USD", "name": "US Dollar"},
]


class FakeResponse:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise ValueError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


class TestResCurrencyRateProviderFrankfurter(BaseCommon):
    """Only the HTTP call to api.frankfurter.dev is mocked; the rest of the
    flow (provider record, update wizard, rate creation) is the real one."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.jod_currency = cls.env.ref("base.JOD")
        cls.company = cls.env["res.company"].create(
            {"name": "Test company", "currency_id": cls.eur_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.provider = cls.env["res.currency.rate.provider"].create(
            {
                "service": "frankfurter",
                "currency_ids": [Command.set([cls.usd_currency.id])],
            }
        )

    def setUp(self):
        super().setUp()
        # ``_fetch_supported_currencies_frankfurter`` is ormcached
        self.env.registry.clear_cache()
        self.addCleanup(self.env.registry.clear_cache)

    def _mock_get(self, rates_payload, currencies_payload=None):
        """Dispatch the mocked HTTP GET on the Frankfurter endpoint."""
        if currencies_payload is None:
            currencies_payload = CURRENCIES_PAYLOAD
        self.requests = []

        def _side_effect(url, params=None, timeout=None):
            self.requests.append((url, params or {}))
            if url.endswith("/currencies"):
                return FakeResponse(currencies_payload)
            return FakeResponse(rates_payload)

        return mock.patch(_REQUESTS_GET, side_effect=_side_effect)

    def _run_wizard(self, vals=None):
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[Command.set([self.provider.id])])
            .create(vals or {})
        )
        wizard.action_update()
        return wizard

    def test_supported_currencies(self):
        with self._mock_get([]):
            currencies = self.provider._get_supported_currencies()
        self.assertIn("JOD", currencies)
        self.assertIn("USD", currencies)
        # The endpoint is the v2 currencies one, asked once and then cached
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(
            self.requests[0][0], "https://api.frankfurter.dev/v2/currencies"
        )
        with self._mock_get([]):
            self.provider._get_supported_currencies()
        self.assertFalse(self.requests, "the cached value was not reused")

    def test_supported_currencies_other_service_untouched(self):
        """A provider of another service must not reach Frankfurter."""
        ecb_provider = self.env["res.currency.rate.provider"].create(
            {"service": "ECB", "currency_ids": [Command.set([self.usd_currency.id])]}
        )
        with self._mock_get([]):
            ecb_provider._get_supported_currencies()
        self.assertFalse(self.requests)

    @freeze_time("2026-10-19")
    @mute_logger("odoo.models.unlink")
    def test_wizard_single_date(self):
        self.usd_currency.rate_ids.unlink()
        rates_payload = [{"date": "2026-10-19", "quote": "USD", "rate": 1.0865}]
        with self._mock_get(rates_payload):
            self._run_wizard()
        self.assertEqual(len(self.usd_currency.rate_ids), 1)
        self.assertEqual(
            self.usd_currency.rate_ids.name, fields.Date.from_string("2026-10-19")
        )
        self.assertAlmostEqual(self.usd_currency.rate_ids.rate, 1.0865, places=4)
        rates_url, params = self.requests[-1]
        self.assertEqual(rates_url, "https://api.frankfurter.dev/v2/rates")
        self.assertEqual(params["base"], "EUR")
        self.assertEqual(params["quotes"], "USD")
        self.assertEqual(params["date"], "2026-10-19")
        self.assertNotIn("from", params)

    @freeze_time("2026-10-19")
    @mute_logger("odoo.models.unlink")
    def test_wizard_date_range(self):
        self.jod_currency.active = True
        self.jod_currency.rate_ids.unlink()
        self.provider.write({"currency_ids": [Command.set([self.jod_currency.id])]})
        rates_payload = [
            {"date": "2026-10-15", "quote": "JOD", "rate": 0.8213},
            {"date": "2026-10-16", "quote": "JOD", "rate": 0.8230},
        ]
        with self._mock_get(rates_payload):
            self._run_wizard({"date_from": "2026-10-15", "date_to": "2026-10-16"})
        rate_dates = self.jod_currency.rate_ids.mapped("name")
        self.assertEqual(len(self.jod_currency.rate_ids), 2)
        self.assertIn(fields.Date.from_string("2026-10-15"), rate_dates)
        self.assertIn(fields.Date.from_string("2026-10-16"), rate_dates)
        params = self.requests[-1][1]
        self.assertEqual(params["from"], "2026-10-15")
        self.assertEqual(params["to"], "2026-10-16")
        self.assertNotIn("date", params)

    @freeze_time("2026-10-19")
    @mute_logger("odoo.models.unlink")
    def test_wizard_company_currency_as_base(self):
        """The company currency is the base sent to the API, not a fixed EUR."""
        self.company.currency_id = self.usd_currency
        self.jod_currency.active = True
        self.jod_currency.rate_ids.unlink()
        self.provider.write({"currency_ids": [Command.set([self.jod_currency.id])]})
        rates_payload = [{"date": "2026-10-19", "quote": "JOD", "rate": 0.7090}]
        with self._mock_get(rates_payload):
            self._run_wizard()
        self.assertEqual(self.requests[-1][1]["base"], "USD")
        self.assertEqual(len(self.jod_currency.rate_ids), 1)

    def test_rates_only_base_currency_requested(self):
        """Nothing is asked to the API when only the base currency is given."""
        with self._mock_get([]):
            result = self.provider._obtain_rates(
                "EUR",
                ["EUR"],
                fields.Date.from_string("2026-10-19"),
                fields.Date.from_string("2026-10-19"),
            )
        self.assertEqual(result, {})
        self.assertFalse(self.requests)

    def test_http_error_raises_user_error(self):
        with mock.patch(_REQUESTS_GET, return_value=FakeResponse(None, 503)):
            with self.assertRaises(UserError):
                self.provider._obtain_rates(
                    "EUR",
                    ["USD"],
                    fields.Date.from_string("2026-10-19"),
                    fields.Date.from_string("2026-10-19"),
                )

    @mute_logger(
        "odoo.addons.currency_rate_update_frankfurter.models.res_currency_rate_provider"
    )
    def test_supported_currencies_http_error_is_logged(self):
        with mock.patch(_REQUESTS_GET, return_value=FakeResponse(None, 503)):
            self.assertEqual(self.provider._get_supported_currencies(), [])
