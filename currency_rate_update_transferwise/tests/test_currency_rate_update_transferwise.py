# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from unittest import mock
from urllib.error import HTTPError

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

_module_ns = 'odoo.addons.currency_rate_update_transferwise'
_provider_class = (
    _module_ns
    + '.models.res_currency_rate_provider_TransferWise'
    + '.ResCurrencyRateProviderTransferWise'
)


class TestResCurrencyRateProviderTransferWise(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Company = self.env['res.company']
        self.CurrencyRate = self.env['res.currency.rate']
        self.CurrencyRateProvider = self.env['res.currency.rate.provider']

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref('base.EUR')
        self.transferwise_provider = self.CurrencyRateProvider.create({
            'service': 'TransferWise',
            'currency_ids': [
                (4, self.eur_currency.id),
            ],
        })
        self.CurrencyRate.search([]).unlink()

    def test_supported_currencies(self):
        mocked_response = (
            """[
    {
        "rate": 1.0,
        "source": "EUR",
        "target": "EUR",
        "time": "2019-01-01T00:00:00+0000"
    }
]""")
        supported_currencies = []
        with mock.patch(
            _provider_class + '._transferwise_provider_retrieve',
            return_value=mocked_response,
        ):
            supported_currencies = (
                self.transferwise_provider._get_supported_currencies()
            )
        self.assertEqual(len(supported_currencies), 1)

    def test_update(self):
        date = self.today - relativedelta(days=1)
        mocked_response = (
            """[
    {
        "rate": 0.86995,
        "source": "USD",
        "target": "EUR",
        "time": "%(date)sT00:00:00+0000"
    }
]""" % {
                'date': str(date),
            })
        with mock.patch(
            _provider_class + '._transferwise_provider_retrieve',
            return_value=mocked_response,
        ):
            self.transferwise_provider._update(date, date)

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ], limit=1)
        self.assertTrue(rates)

        self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ]).unlink()

    def test_no_credentials(self):
        self.env.user.company_id.transferwise_api_key = None
        with self.assertRaises(UserError):
            self.transferwise_provider._get_supported_currencies()

    def test_bad_credentials(self):
        self.env.user.company_id.transferwise_api_key = 'bad'
        with self.assertRaises(HTTPError):
            self.transferwise_provider._obtain_rates(
                'USD',
                ['EUR'],
                self.today,
                self.today,
            )
