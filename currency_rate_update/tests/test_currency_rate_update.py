# Copyright 2017 Comunitea
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo.tests import common
from odoo import fields


class TestCurrencyRateUpdate(common.SavepointCase):

    def setUp(self):
        super().setUp()

        self.Company = self.env['res.company']
        self.CurrencyRate = self.env['res.currency.rate']
        self.CurrencyRateProvider = self.env['res.currency.rate.provider']

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref('base.EUR')
        self.usd_currency = self.env.ref('base.USD')
        self.company = self.Company.create({
            'name': 'Test company',
            'currency_id': self.eur_currency.id,
        })
        self.env.user.company_ids += self.company
        self.env.user.company_id = self.company
        self.ecb_provider = self.CurrencyRateProvider.create({
            'service': 'ECB',
            'currency_ids': [
                (4, self.usd_currency.id),
                (4, self.env.user.company_id.currency_id.id),
            ],
        })
        self.CurrencyRate.search([]).unlink()

    def test_update_ECB_today(self):
        """No checks are made since today may not be a banking day"""
        self.ecb_provider._update(self.today, self.today)
        self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ]).unlink()

    def test_update_ECB_month(self):
        self.ecb_provider._update(
            self.today - relativedelta(months=1),
            self.today
        )

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ], limit=1)
        self.assertTrue(rates)

        self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ]).unlink()

    def test_update_ECB_year(self):
        self.ecb_provider._update(
            self.today - relativedelta(years=1),
            self.today
        )

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ], limit=1)
        self.assertTrue(rates)

        self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ]).unlink()

    def test_update_ECB_scheduled(self):
        self.ecb_provider.next_run = fields.Date.today()
        self.ecb_provider._scheduled_update()

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ])
        self.assertEquals(len(rates), 1)

        self.CurrencyRate.search([
            ('currency_id', '=', self.usd_currency.id),
        ]).unlink()

    def test_update_ECB_no_base_update(self):
        self.ecb_provider.next_run = fields.Date.today()
        self.ecb_provider._scheduled_update()

        rates = self.CurrencyRate.search([
            ('company_id', '=', self.company.id),
            ('currency_id', 'in', [
                self.usd_currency.id,
                self.eur_currency.id,
            ]),
        ])
        self.assertEquals(len(rates), 1)

        self.CurrencyRate.search([
            ('company_id', '=', self.company.id),
        ]).unlink()
