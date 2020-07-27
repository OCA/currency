# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from unittest import mock
from urllib.error import HTTPError

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

_module_ns = 'odoo.addons.currency_rate_update_oxr'
_provider_class = (
    _module_ns
    + '.models.res_currency_rate_provider_OXR'
    + '.ResCurrencyRateProviderOXR'
)


class TestResCurrencyRateProviderOXR(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Company = self.env['res.company']
        self.CurrencyRate = self.env['res.currency.rate']
        self.CurrencyRateProvider = self.env['res.currency.rate.provider']

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref('base.EUR')
        self.oxr_provider = self.CurrencyRateProvider.create({
            'service': 'OXR',
            'currency_ids': [
                (4, self.eur_currency.id),
            ],
        })
        self.CurrencyRate.search([]).unlink()

    def test_supported_currencies(self):
        mocked_response = (
            """{
    "EUR": "Euro"
}"""
        )
        supported_currencies = []
        with mock.patch(
            _provider_class + '._oxr_provider_retrieve',
            return_value=mocked_response,
        ):
            supported_currencies = (
                self.oxr_provider._get_supported_currencies()
            )
        self.assertEqual(len(supported_currencies), 1)

    def test_update(self):
        date = self.today - relativedelta(days=1)
        mocked_response = (
            """{
    "rates": {
        "EUR": 0.832586
    }
}""" % {
                'date': str(date),
            })
        with mock.patch(
            _provider_class + '._oxr_provider_retrieve',
            return_value=mocked_response,
        ):
            self.oxr_provider._update(date, date)

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ], limit=1)
        self.assertTrue(rates)

        self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ]).unlink()

    def test_no_credentials(self):
        self.env.user.company_id.openexchangerates_app_id = None
        with self.assertRaises(UserError):
            self.oxr_provider._get_supported_currencies()

    def test_bad_credentials(self):
        self.env.user.company_id.openexchangerates_app_id = 'bad'
        with self.assertRaises(HTTPError):
            self.oxr_provider._obtain_rates(
                'USD',
                ['EUR'],
                self.today,
                self.today,
            )
