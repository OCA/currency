from datetime import date
from unittest import mock

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

_module_ns = "odoo.addons.currency_rate_update_vietcombank"
_file_ns = _module_ns + ".models.res_currency_rate_provider_VCB"
_VCB_provider_class = _file_ns + ".ResCurrencyRateProviderVCB"


@tagged("post_install", "-at_install")
class TestCurrencyRateUpdate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Company = cls.env["res.company"]
        cls.CurrencyRate = cls.env["res.currency.rate"]
        cls.CurrencyRateProvider = cls.env["res.currency.rate.provider"]

        cls.today = fields.Date.today()
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.vnd_currency = cls.env.ref("base.VND")
        cls.company = cls.Company.create(
            {"name": "Test company", "currency_id": cls.eur_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.user.company_id = cls.company
        cls.VCB_provider = cls.CurrencyRateProvider.create(
            {
                "service": "VCB",
                "currency_ids": [
                    (4, cls.usd_currency.id),
                    (4, cls.env.user.company_id.currency_id.id),
                ],
            }
        )
        cls.CurrencyRate.search([]).unlink()

    def test_supported_currencies_VCB(self):
        self.VCB_provider._get_supported_currencies()

    def test_error_VCB(self):
        with mock.patch(_VCB_provider_class + "._obtain_rates", return_value=None):
            self.VCB_provider._update(self.today, self.today)

    def test_update_VCB_today(self):
        """No checks are made since today may not be a banking day"""
        self.VCB_provider._update(self.today, self.today)
        self.CurrencyRate.search([("currency_id", "=", self.usd_currency.id)]).unlink()

    def test_update_VCB_month(self):
        self.VCB_provider._update(self.today - relativedelta(months=1), self.today)

        rates = self.CurrencyRate.search(
            [("currency_id", "=", self.usd_currency.id)], limit=1
        )
        self.assertTrue(rates)

        self.CurrencyRate.search([("currency_id", "=", self.usd_currency.id)]).unlink()

    def test_update_VCB_year(self):
        self.VCB_provider._update(self.today - relativedelta(years=1), self.today)

        rates = self.CurrencyRate.search(
            [("currency_id", "=", self.usd_currency.id)], limit=1
        )
        self.assertTrue(rates)

        self.CurrencyRate.search([("currency_id", "=", self.usd_currency.id)]).unlink()

    def test_update_VCB_scheduled(self):
        self.VCB_provider.interval_type = "days"
        self.VCB_provider.interval_number = 14
        self.VCB_provider.next_run = self.today - relativedelta(days=1)
        self.VCB_provider._scheduled_update()

        rates = self.CurrencyRate.search(
            [("currency_id", "=", self.usd_currency.id)], limit=1
        )
        self.assertTrue(rates)

        self.CurrencyRate.search([("currency_id", "=", self.usd_currency.id)]).unlink()

    def test_update_VCB_no_base_update(self):
        self.VCB_provider.interval_type = "days"
        self.VCB_provider.interval_number = 14
        self.VCB_provider.next_run = self.today - relativedelta(days=1)
        self.VCB_provider._scheduled_update()

        rates = self.CurrencyRate.search(
            [
                ("company_id", "=", self.company.id),
                ("currency_id", "in", [self.usd_currency.id, self.eur_currency.id]),
            ],
            limit=1,
        )
        self.assertTrue(rates)

        self.CurrencyRate.search([("company_id", "=", self.company.id)]).unlink()

    def test_update_VCB_sequence(self):
        self.VCB_provider.interval_type = "days"
        self.VCB_provider.interval_number = 1
        self.VCB_provider.last_successful_run = None
        self.VCB_provider.next_run = date(2019, 4, 1)

        self.VCB_provider._scheduled_update()
        self.assertEqual(self.VCB_provider.last_successful_run, date(2019, 4, 1))
        self.assertEqual(self.VCB_provider.next_run, date(2019, 4, 2))
        rates = self.CurrencyRate.search(
            [
                ("company_id", "=", self.company.id),
                ("currency_id", "=", self.usd_currency.id),
            ]
        )
        self.assertEqual(len(rates), 1)

        self.VCB_provider._scheduled_update()
        self.assertEqual(self.VCB_provider.last_successful_run, date(2019, 4, 2))
        self.assertEqual(self.VCB_provider.next_run, date(2019, 4, 3))
        rates = self.CurrencyRate.search(
            [
                ("company_id", "=", self.company.id),
                ("currency_id", "=", self.usd_currency.id),
            ]
        )
        self.assertEqual(len(rates), 2)

        self.CurrencyRate.search([("company_id", "=", self.company.id)]).unlink()

    def test_update_VCB_weekend(self):
        self.VCB_provider.interval_type = "days"
        self.VCB_provider.interval_number = 1
        self.VCB_provider.last_successful_run = None
        self.VCB_provider.next_run = date(2019, 7, 1)

        self.VCB_provider._scheduled_update()
        self.VCB_provider._scheduled_update()
        self.VCB_provider._scheduled_update()
        self.VCB_provider._scheduled_update()
        self.VCB_provider._scheduled_update()

        self.assertEqual(self.VCB_provider.last_successful_run, date(2019, 7, 5))
        self.assertEqual(self.VCB_provider.next_run, date(2019, 7, 6))

        self.VCB_provider._scheduled_update()
        self.VCB_provider._scheduled_update()

        self.assertEqual(self.VCB_provider.last_successful_run, date(2019, 7, 7))
        self.assertEqual(self.VCB_provider.next_run, date(2019, 7, 8))

    def test_foreign_base_currency(self):
        self.company.currency_id = self.vnd_currency
        self.test_update_VCB_today()
        self.test_update_VCB_month()
        self.test_update_VCB_year()
        self.test_update_VCB_scheduled()
        self.test_update_VCB_no_base_update()
        self.test_update_VCB_sequence()
        self.test_update_VCB_weekend()
        self.company.currency_id = self.eur_currency
