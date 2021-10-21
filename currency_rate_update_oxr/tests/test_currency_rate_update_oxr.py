# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from unittest import mock
from urllib.error import HTTPError
import json

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
        self.usd_currency = self.env.ref('base.USD')
        self.oxr_provider = self.CurrencyRateProvider.create({
            'service': 'OXR',
            'currency_ids': [
                (4, self.eur_currency.id),
                (4, self.usd_currency.id),
            ],
        })
        self.CurrencyRate.search([]).unlink()

    def test_supported_currencies(self):
        mocked_response = (
            """{
    "EUR": "Euro",
    "USD": "United States Dollar"
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
        self.assertEqual(len(supported_currencies), 2)

    def test_update(self):
        date = self.today - relativedelta(days=1)
        mocked_response = (
            """{
                "rates": {
                    "EUR": 1.0,
                    "USD": 1.16
                 },
                "timestamp": 1634311833
            }"""
        )
        with mock.patch(
            _provider_class + '._oxr_provider_retrieve',
            return_value=mocked_response,
        ):
            self.oxr_provider._update(date, date)

        if self.env.user.company_id.currency_id == self.eur_currency:
            currency = self.usd_currency
        else:
            currency = self.eur_currency

        # If the mocked currency is the same as the company currency
        # it wil not be created.
        rates = self.CurrencyRate.search([
            ('currency_id', '=', currency.id),
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

    def test_wrong_rate(self):
        """Receive today's rate when expecting yesterday's end-of-day rate."""
        self.env.user.company_id.openexchangerates_eod_rates = True
        date = self.today - relativedelta(days=1)
        mocked_response = json.dumps({
            "rates": {
                "EUR": 1.0,
                "USD": 1.16
             },
            "timestamp": int(date.strftime('%s'))
        })

        with mock.patch(
            _provider_class + '._oxr_provider_retrieve',
            return_value=mocked_response,
        ):
            with self.assertLogs(logger=None, level='WARNING') as log:
                self.oxr_provider._update(date, date)
            self.assertIn('Exchange rate from incorrect date received', log.output[0])
