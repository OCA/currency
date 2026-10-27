# Copyright 2026 AllRatesToday (https://allratestoday.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest import mock

from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

MODULE = "odoo.addons.currency_rate_update_allratestoday.models"
GET = f"{MODULE}.res_currency_rate_provider_allratestoday.requests.get"

# ECB style: home currency on the base side.
ECB_LATEST = {
    "bank": "ecb",
    "rate_date": "2026-10-27",
    "rates": [
        {"base": "EUR", "quote": "USD", "type": "reference", "value": 1.16},
        {"base": "EUR", "quote": "GBP", "type": "reference", "value": 0.84},
        {"base": "EUR", "quote": "JPY", "type": "reference", "value": 178.0},
    ],
}
ECB_FRIDAY = {
    "bank": "ecb",
    "rate_date": "2026-10-23",
    "rates": [
        {"base": "EUR", "quote": "USD", "type": "reference", "value": 1.15},
        {"base": "EUR", "quote": "GBP", "type": "reference", "value": 0.85},
    ],
}
# RBI style: home currency on the quote side, several series per pair.
RBI_LATEST = {
    "bank": "rbi",
    "rate_date": "2026-10-27",
    "rates": [
        {"base": "USD", "quote": "INR", "type": "reference", "value": 88.0},
        {"base": "EUR", "quote": "INR", "type": "reference", "value": 102.08},
        {"base": "EUR", "quote": "INR", "type": "buy", "value": 101.0},
    ],
}


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class TestResCurrencyRateProviderAllRatesToday(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.CurrencyRate = cls.env["res.currency.rate"]
        cls.CurrencyRateProvider = cls.env["res.currency.rate.provider"]
        cls.eur = cls.env.ref("base.EUR")
        cls.usd = cls.env.ref("base.USD")
        cls.gbp = cls.env.ref("base.GBP")
        cls.inr = cls.env.ref("base.INR")
        (cls.usd + cls.gbp + cls.inr).write({"active": True})
        cls.company = cls.Company.create(
            {"name": "Test company", "currency_id": cls.eur.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.CurrencyRate.search([]).unlink()

    def _provider(self, bank="ecb", key="", currencies=None, rate_type=""):
        currencies = currencies or (self.usd + self.gbp)
        with mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)):
            return self.CurrencyRateProvider.create(
                {
                    "service": "AllRatesToday",
                    "allratestoday_bank": bank,
                    "allratestoday_api_key": key,
                    "allratestoday_rate_type": rate_type,
                    "company_id": self.company.id,
                    "currency_ids": [(6, 0, currencies.ids)],
                }
            )

    def test_supported_currencies_from_latest_table(self):
        provider = self._provider()
        with mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)) as get:
            codes = provider._get_supported_currencies()
        self.assertEqual(codes, ["EUR", "GBP", "JPY", "USD"])
        self.assertIn("/api/open/central-bank/ecb", get.call_args[0][0])

    @freeze_time("2026-10-27")
    def test_cron_latest_keyless(self):
        provider = self._provider()
        with mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)) as get:
            provider._scheduled_update()
        self.assertEqual(get.call_count, 1)
        rates = self.CurrencyRate.search([("company_id", "=", self.company.id)])
        self.assertEqual(len(rates), 2)
        usd = rates.filtered(lambda r: r.currency_id == self.usd)
        self.assertEqual(usd.name, fields.Date.from_string("2026-10-27"))
        self.assertAlmostEqual(usd.rate, 1.16, places=6)

    @freeze_time("2026-10-27")
    def test_keyed_latest_uses_v1_endpoint(self):
        provider = self._provider(key="art_live_test")
        with mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)) as get:
            provider._scheduled_update()
        urls = [c[0][0] for c in get.call_args_list]
        self.assertTrue(any("/api/v1/central-bank/ecb/latest" in u for u in urls))
        for call in get.call_args_list:
            self.assertEqual(
                call[1]["headers"]["Authorization"], "Bearer art_live_test"
            )

    @freeze_time("2026-10-27")
    def test_rebase_when_home_currency_is_quote_side(self):
        # Company in EUR, publisher RBI (INR on the quote side, buy/reference
        # series for EUR). 1 EUR = 102.08 INR -> 1 EUR = 102.08/88 USD.
        provider = self._provider(bank="rbi", currencies=self.usd + self.inr)
        with mock.patch(GET, return_value=FakeResponse(200, RBI_LATEST)):
            provider._scheduled_update()
        rates = self.CurrencyRate.search([("company_id", "=", self.company.id)])
        by_ccy = {r.currency_id.name: r.rate for r in rates}
        self.assertAlmostEqual(by_ccy["INR"], 102.08, places=6)
        self.assertAlmostEqual(by_ccy["USD"], 102.08 / 88.0, places=6)

    @freeze_time("2026-10-27")
    def test_pinned_rate_type(self):
        provider = self._provider(bank="rbi", currencies=self.inr, rate_type="buy")
        with mock.patch(GET, return_value=FakeResponse(200, RBI_LATEST)):
            provider._scheduled_update()
        inr = self.CurrencyRate.search(
            [("company_id", "=", self.company.id), ("currency_id", "=", self.inr.id)]
        )
        self.assertAlmostEqual(inr.rate, 101.0, places=6)

    @freeze_time("2026-10-27")
    def test_wizard_range_walks_dated_endpoint(self):
        provider = self._provider(key="art_live_test")

        def fake_get(url, **kw):
            if url.endswith("/latest"):
                return FakeResponse(200, ECB_LATEST)
            # Dated endpoint answers with the newest table on or before the day.
            day = url.rsplit("/", 1)[1]
            if day >= "2026-10-27":
                return FakeResponse(200, ECB_LATEST)
            if day >= "2026-10-23":
                return FakeResponse(200, ECB_FRIDAY)
            return FakeResponse(404)

        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, provider.ids)])
            .create({"date_from": "2026-10-22", "date_to": "2026-10-27"})
        )
        with mock.patch(GET, side_effect=fake_get) as get:
            wizard.action_update()
        # latest + 26th (-> Friday table) + 22nd (404); 25th/24th/23rd skipped by
        # the jump back to the day before the Friday table.
        self.assertEqual(get.call_count, 3)
        usd_dates = self.usd.rate_ids.filtered(
            lambda r: r.company_id == self.company
        ).mapped("name")
        self.assertEqual(
            sorted(usd_dates),
            [
                fields.Date.from_string("2026-10-23"),
                fields.Date.from_string("2026-10-27"),
            ],
        )

    @freeze_time("2026-10-27")
    def test_keyless_range_serves_latest_only(self):
        # The cron asks from the day after the last run; without a key the
        # latest table is served and older days are skipped, not refused.
        provider = self._provider()
        with mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)) as get:
            content = provider._obtain_rates(
                "EUR",
                ["USD"],
                fields.Date.from_string("2026-10-20"),
                fields.Date.from_string("2026-10-27"),
            )
        self.assertEqual(get.call_count, 1)
        self.assertEqual(list(content), ["2026-10-27"])

    @freeze_time("2026-10-27")
    def test_purely_past_range_without_key_is_refused(self):
        provider = self._provider()
        with (
            mock.patch(GET, return_value=FakeResponse(200, ECB_LATEST)),
            self.assertRaises(UserError),
        ):
            provider._obtain_rates(
                "EUR",
                ["USD"],
                fields.Date.from_string("2026-10-20"),
                fields.Date.from_string("2026-10-24"),
            )

    def test_bad_bank_code(self):
        provider = self._provider()
        provider.allratestoday_bank = "not a code"
        with self.assertRaises(UserError):
            provider._get_supported_currencies()

    def test_http_errors_are_user_errors(self):
        provider = self._provider(key="art_live_test")
        for status in (401, 403, 500):
            with (
                mock.patch(GET, return_value=FakeResponse(status, text="x")),
                self.assertRaises(UserError),
            ):
                provider._get_supported_currencies()
