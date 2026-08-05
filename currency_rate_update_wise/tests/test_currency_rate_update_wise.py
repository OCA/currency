# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2026 Altixia (https://altixia.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date
from unittest import mock

import requests
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

from ..models import res_currency_rate_provider_Wise as wise_mod

_module_ns = "odoo.addons.currency_rate_update_wise"
_provider_class = (
    _module_ns
    + ".models.res_currency_rate_provider_Wise"
    + ".ResCurrencyRateProviderWise"
)
_retrieve = _provider_class + "._wise_provider_retrieve"


class TestResCurrencyRateProviderWise(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.Company = self.env["res.company"]
        self.CurrencyRate = self.env["res.currency.rate"]
        self.CurrencyRateProvider = self.env["res.currency.rate.provider"]

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref("base.EUR")
        self.wise_provider = self.CurrencyRateProvider.create(
            {"service": "Wise", "currency_ids": [(4, self.eur_currency.id)]}
        )
        self.env.user.company_id.wise_api_key = "test-token"
        self.CurrencyRate.search([]).unlink()

    def test_supported_currencies(self):
        mocked_response = [
            {
                "rate": 1.0,
                "source": "EUR",
                "target": "EUR",
                "time": "2019-01-01T00:00:00+0000",
            }
        ]
        with mock.patch(_retrieve, return_value=mocked_response):
            supported_currencies = self.wise_provider._get_supported_currencies()
        self.assertEqual(len(supported_currencies), 1)

    def test_update(self):
        # Odoo never stores a rate for the company's own currency. Pin an EUR
        # company and fetch a foreign currency (USD) so a rate row is actually
        # created, regardless of the default company currency of the series.
        usd_currency = self.env.ref("base.USD")
        company = self.Company.create(
            {"name": "Wise Test Co", "currency_id": self.eur_currency.id}
        )
        self.env.user.company_ids += company
        company.wise_api_key = "test-token"
        provider = self.CurrencyRateProvider.with_company(company).create(
            {"service": "Wise", "currency_ids": [(4, usd_currency.id)]}
        )
        date = self.today - relativedelta(days=1)
        mocked_response = [
            {
                "rate": 1.15,
                "source": "EUR",
                "target": "USD",
                "time": str(date) + "T00:00:00+0000",
            }
        ]
        with mock.patch(_retrieve, return_value=mocked_response):
            provider.with_company(company)._update(date, date)

        rates = self.CurrencyRate.search([("currency_id", "=", usd_currency.id)])
        self.assertTrue(rates)

    def test_single_day_window_is_widened(self):
        # Wise answers HTTP 400 when "from" equals "to", which is exactly what
        # a scheduled run asks for once the rates are up to date. The provider
        # must widen the window instead of sending a zero-length range.
        captured = []

        def _capture(_self, _url, params=None):
            captured.append(params)
            return []

        with mock.patch(_retrieve, _capture):
            self.wise_provider._obtain_rates("USD", ["EUR"], self.today, self.today)

        self.assertTrue(captured, "no request was issued")
        for params in captured:
            self.assertNotEqual(
                params["from"],
                params["to"],
                "Wise rejects a zero-length window with HTTP 400",
            )
            self.assertEqual(params["from"], str(self.today))

    def test_no_credentials(self):
        self.env.user.company_id.wise_api_key = None
        with self.assertRaises(UserError):
            self.wise_provider._get_supported_currencies()

    def test_bad_credentials(self):
        # Hermetic: simulate Wise returning an HTTP error, no real network call.
        with (
            mock.patch(_retrieve, side_effect=requests.exceptions.HTTPError("401")),
            self.assertRaises(requests.exceptions.HTTPError),
        ):
            self.wise_provider._obtain_rates("USD", ["EUR"], self.today, self.today)

    def test_error_response(self):
        # An API error payload must raise a clean UserError.
        with (
            mock.patch(
                _retrieve,
                return_value={"error": True, "error_description": "boom"},
            ),
            self.assertRaises(UserError),
        ):
            self.wise_provider._get_supported_currencies()

    def _warn_calls(self, today):
        # Run the legacy-token check at a given date, return the logger mock.
        with (
            mock.patch.object(wise_mod.fields.Date, "today", return_value=today),
            mock.patch.object(wise_mod._logger, "warning") as warn,
        ):
            self.wise_provider._wise_warn_legacy_tokens()
        return warn

    def test_legacy_uuid_token_warning(self):
        # UUID token, on/after JWT availability -> warning.
        self.env.user.company_id.wise_api_key = "ca44a17e-9b28-4fb7-bcf7-9ba09340c26f"
        self.assertTrue(self._warn_calls(date(2026, 8, 1)).called)

    def test_no_warning_before_jwt_availability(self):
        # UUID token, before JWT is available -> no warning (not actionable).
        self.env.user.company_id.wise_api_key = "ca44a17e-9b28-4fb7-bcf7-9ba09340c26f"
        self.assertFalse(self._warn_calls(date(2026, 7, 15)).called)

    def test_no_warning_after_window(self):
        # UUID token, after the migration window closed -> no warning.
        self.env.user.company_id.wise_api_key = "ca44a17e-9b28-4fb7-bcf7-9ba09340c26f"
        self.assertFalse(self._warn_calls(date(2027, 8, 1)).called)

    def test_no_warning_without_token(self):
        # No key configured -> no warning.
        self.env.user.company_id.wise_api_key = False
        self.assertFalse(self._warn_calls(date(2026, 8, 1)).called)

    def test_no_warning_for_jwt_token(self):
        # A JWT-format token is the target format -> no warning.
        self.env.user.company_id.wise_api_key = "eyJhbGci.eyJzdWIi.sig"
        self.assertFalse(self._warn_calls(date(2026, 8, 1)).called)
