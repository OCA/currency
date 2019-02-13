# Copyright 2009 Camptocamp
# Copyright 2009 Grzegorz Grzelak
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import date, timedelta
from urllib.request import urlopen
import xml.sax

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderECB(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('ECB', 'European Central Bank')],
    )

    @api.model
    def _get_supported_currencies(self, service):
        if service == 'ECB':
            # https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip
            return \
                [
                    'USD', 'JPY', 'BGN', 'CYP', 'CZK', 'DKK', 'EEK', 'GBP',
                    'HUF', 'LTL', 'LVL', 'MTL', 'PLN', 'ROL', 'RON', 'SEK',
                    'SIT', 'SKK', 'CHF', 'ISK', 'NOK', 'HRK', 'RUB', 'TRL',
                    'TRY', 'AUD', 'BRL', 'CAD', 'CNY', 'HKD', 'IDR', 'ILS',
                    'INR', 'KRW', 'MXN', 'MYR', 'NZD', 'PHP', 'SGD', 'THB',
                    'ZAR',
                ]
        return super()._get_supported_currencies(service)

    @api.model
    def _obtain_rates(self, service, base_currency, currencies, date_from,
                      date_to):
        if service == 'ECB':
            if base_currency != 'EUR':
                raise UserError(_(
                    'European Central Bank is suitable only for companies'
                    ' with EUR as base currency!'
                ))

            url = 'https://www.ecb.europa.eu/stats/eurofxref'
            if date_from == date_to and date_from == date.today():
                url = url + '/eurofxref-daily.xml'
            elif (date.today() - date_from) / timedelta(days=90) < 1.0:
                url = url + '/eurofxref-hist-90d.xml'
            else:
                url = url + '/eurofxref-hist.xml'

            handler = EcbRatesHandler(currencies, date_from, date_to)
            with urlopen(url) as response:
                xml.sax.parse(response, handler)

            return handler.content

        return super()._obtain_rates(service, base_currency, currencies,
                                     date_from, date_to)


class EcbRatesHandler(xml.sax.ContentHandler):
    def __init__(self, currencies, date_from, date_to):
        self.currencies = currencies
        self.date_from = date_from
        self.date_to = date_to
        self.date = None
        self.content = defaultdict(dict)

    def startElement(self, name, attrs):
        if name == 'Cube' and 'time' in attrs:
            self.date = fields.Date.from_string(attrs['time'])
        elif name == 'Cube' and \
                all([x in attrs for x in ['currency', 'rate']]):
            currency = attrs['currency']
            rate = attrs['rate']

            if (self.date_from is None or self.date >= self.date_from) and \
                    (self.date_to is None or self.date <= self.date_to) and \
                    currency in self.currencies:
                self.content[self.date.isoformat()][currency] = rate
