# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from io import StringIO
from unittest import mock

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import common

_module_ns = 'odoo.addons.currency_rate_update_xe'
_provider_class = (
    _module_ns
    + '.models.res_currency_rate_provider_XE'
    + '.ResCurrencyRateProviderXE'
)


class TestResCurrencyRateProviderXE(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Company = self.env['res.company']
        self.CurrencyRate = self.env['res.currency.rate']
        self.CurrencyRateProvider = self.env['res.currency.rate.provider']

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref('base.EUR')
        self.xe_provider = self.CurrencyRateProvider.create({
            'service': 'XE',
            'currency_ids': [
                (4, self.eur_currency.id),
            ],
        })
        self.CurrencyRate.search([]).unlink()

    def test_supported_currencies(self):
        mocked_response = (
            """<?xml version="1.0" ?>
<currencies
    xmlns="http://xecdapi.xe.com"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://xecdapi.xe.com/schema/v1/currencies.xsd"
>
    <terms>http://www.xe.com/legal/dfs.php</terms>
    <privacy>http://www.xe.com/privacy.php</privacy>
    <currencies>
        <currency>
            <currencyCode>EUR</currencyCode>
            <currencyName>Euro</currencyName>
            <obsolete>false</obsolete>
        </currency>
    </currencies>
</currencies>"""
        )
        supported_currencies = []
        with mock.patch(
            _provider_class + '._xe_provider_urlopen',
            return_value=StringIO(mocked_response),
        ):
            supported_currencies = (
                self.xe_provider._get_supported_currencies()
            )
        self.assertEqual(len(supported_currencies), 1)

    def test_update(self):
        date = self.today - relativedelta(days=1)
        mocked_response = (
            """<?xml version="1.0" ?>
<historicRatePeriod
    xmlns="http://xecdapi.xe.com"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://xecdapi.xe.com/schema/v1/historicRatePeriod.xsd"
>
    <terms>http://www.xe.com/legal/dfs.php</terms>
    <privacy>http://www.xe.com/privacy.php</privacy>
    <from>USD</from>
    <amount>1.0</amount>
    <to>
        <entry>
            <string>EUR</string>
            <list>
                <rate>
                    <mid>0.8875884973</mid>
                    <timestamp>%(date)sT00:00:00Z</timestamp>
                </rate>
            </list>
        </entry>
    </to>
</historicRatePeriod>""" % {
                'date': str(date),
            })
        with mock.patch(
            _provider_class + '._xe_provider_urlopen',
            return_value=StringIO(mocked_response),
        ):
            self.xe_provider._update(date, date)

        rates = self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ], limit=1)
        self.assertTrue(rates)

        self.CurrencyRate.search([
            ('currency_id', '=', self.eur_currency.id),
        ]).unlink()

    def test_no_credentials(self):
        with self.assertRaises(UserError):
            self.xe_provider._get_supported_currencies()
