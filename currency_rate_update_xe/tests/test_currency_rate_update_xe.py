# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest import mock

import requests
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

from ..models import res_currency_rate_provider_XE as xe_module

_PROVIDER = (
    "odoo.addons.currency_rate_update_xe.models"
    ".res_currency_rate_provider_XE.ResCurrencyRateProviderXE"
)
_REQUEST_DATA = _PROVIDER + "._request_data"

# Minimal XE.com currency-table HTML matching the provider's xpath
# (//div[@id='table-section']//tbody/tr ; th = currency code ; td[2] = rate).
_XE_HTML = b"""<html><body>
<div id="table-section"><table><tbody>
<tr><th>USD</th><td>US Dollar</td><td>0.920000</td></tr>
<tr><th>GBP</th><td>British Pound</td><td>1.170000</td></tr>
</tbody></table></div>
</body></html>"""


class _FakeResponse:
    """Minimal stand-in for a ``requests`` response (no real network call)."""

    def __init__(self, content=_XE_HTML, status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(self.status_code)


class TestResCurrencyRateProviderXE(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Company = cls.env["res.company"]
        cls.CurrencyRate = cls.env["res.currency.rate"]
        cls.CurrencyRateProvider = cls.env["res.currency.rate.provider"]

        cls.today = fields.Date.today()
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.company = cls.Company.create(
            {"name": "Test company", "currency_id": cls.eur_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.xe_provider = cls.CurrencyRateProvider.create(
            {
                "service": "XE",
                "currency_ids": [
                    (4, cls.usd_currency.id),
                    (4, cls.eur_currency.id),
                ],
            }
        )
        cls.CurrencyRate.search([]).unlink()

    def test_cron(self):
        # Pretend the provider already ran yesterday so the scheduled update
        # only fetches today's rate (via the latest endpoint). Hermetic: the
        # HTTP layer is mocked, no real call to xe.com.
        self.xe_provider.last_successful_run = self.today - relativedelta(days=1)
        with mock.patch(_REQUEST_DATA, return_value=_FakeResponse()):
            self.xe_provider._scheduled_update()
        rates = self.CurrencyRate.search([])
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates.currency_id, self.usd_currency)

    def test_wizard(self):
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, self.xe_provider.ids)])
            .create({})
        )
        with mock.patch(_REQUEST_DATA, return_value=_FakeResponse()):
            wizard.action_update()
        rates = self.CurrencyRate.search([])
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates.currency_id, self.usd_currency)

    def test_parse_data(self):
        # The HTML table is parsed into a {currency: rate} mapping, filtered
        # to the requested currencies only.
        rates = self.xe_provider._parse_data(_FakeResponse(), ["USD"])
        self.assertEqual(rates, {"USD": 0.92})

    def test_today_falls_back_to_latest_endpoint(self):
        # XE.com returns HTTP 404 for ``?date=<today>``; over a range that ends
        # today, the provider must use the dated endpoint for past days and
        # fall back to the latest endpoint (no ``date=``) for today.
        captured = []

        def _capture(url):
            captured.append(url)
            return _FakeResponse()

        yesterday = self.today - relativedelta(days=1)
        with mock.patch(_REQUEST_DATA, side_effect=_capture):
            self.xe_provider._obtain_rates("EUR", ["USD"], yesterday, self.today)
        self.assertEqual(len(captured), 2)
        self.assertIn("date=", captured[0])  # past day -> dated endpoint
        self.assertNotIn("date=", captured[1])  # today -> latest fallback

    def test_http_error_raises_user_error(self):
        # An HTTP error status (e.g. 403/404) surfaces as a clean UserError
        # instead of a raw traceback.
        with mock.patch.object(
            xe_module.requests,
            "request",
            return_value=_FakeResponse(status_code=404),
        ):
            with self.assertRaises(UserError):
                self.xe_provider._request_data(
                    "http://www.xe.com/currencytables/?from=EUR"
                )
