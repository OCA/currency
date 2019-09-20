# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import timedelta
import dateutil.parser
import urllib.request
import xml.sax

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderXE(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('XE', 'XE.com')],
    )

    @api.multi
    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'XE':
            return super()._get_supported_currencies()  # pragma: no cover

        handler = XeComCurrenciesHandler()

        url = 'https://xecdapi.xe.com/v1/currencies.xml'
        with self._xe_provider_urlopen(url) as response:
            xml.sax.parse(response, handler)

        return handler.currencies

    @api.multi
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'XE':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        handler = XeComRatesHandler(currencies, date_from, date_to)

        # NOTE: Step in 100 days is related to max results per page
        step = timedelta(days=100)
        since = date_from
        until = since + step
        page = 1
        while since <= date_to:
            url = (
                'https://xecdapi.xe.com/v1/historic_rate/period.xml' +
                '?from=%(from)s&to=%(to)s&start_timestamp=%(since)s' +
                '&end_timestamp=%(until)s&amount=1.0&interval=daily' +
                '&per_page=100&page=%(page)d'
            ) % {
                'from': base_currency,
                'to': ','.join(currencies),
                'since': str(since),
                'until': str(min(until, date_to)),
                'page': page,
            }

            with self._xe_provider_urlopen(url) as response:
                xml.sax.parse(response, handler)

            since += step
            until += step
            page += 1

        return handler.content

    @api.multi
    def _xe_provider_urlopen(self, url):
        self.ensure_one()

        if not self.company_id.xe_com_account_id or \
                not self.company_id.xe_com_account_api_key:
            raise UserError(_('No XE.com Account credentials specified!'))

        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(
            None,
            'https://xecdapi.xe.com/v1',
            self.company_id.xe_com_account_id,
            self.company_id.xe_com_account_api_key
        )

        auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)

        return urllib.request.build_opener(auth_handler).open(url)


class XeComCurrenciesHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.currencies = list()
        self.tags = list()
        self.currencyCode = None

    def startElement(self, name, attrs):
        self.tags.append(name)

    def characters(self, content):
        name = self.tags[-1] if len(self.tags) >= 1 else None
        parent_name = self.tags[-2] if len(self.tags) >= 2 else None

        if name == 'currencyCode' and parent_name == 'currency':
            self.currencyCode = content

    def endElement(self, name):
        if name == 'currency':
            self.currencies.append(self.currencyCode)
            self.currencyCode = None

        self.tags.pop()


class XeComRatesHandler(xml.sax.ContentHandler):
    def __init__(self, currencies, date_from, date_to):
        self.currencies = currencies
        self.date_from = date_from
        self.date_to = date_to
        self.content = defaultdict(dict)
        self.tags = list()
        self.currency = None
        self.date = None
        self.rate = None
        self.rates = None

    def startElement(self, name, attrs):
        if name == 'entry':
            self.rates = dict()

        self.tags.append(name)

    def characters(self, content):
        name = self.tags[-1] if len(self.tags) >= 1 else None
        parent_name = self.tags[-2] if len(self.tags) >= 2 else None

        if name == 'mid' and parent_name == 'rate':
            self.rate = content
        elif name == 'timestamp' and parent_name == 'rate':
            self.date = dateutil.parser.parse(content).date()
        elif name == 'string' and parent_name == 'entry':
            self.currency = content

    def endElement(self, name):
        if name == 'rate':
            self.rates[self.date] = self.rate
            self.date = None
            self.rate = None
        elif name == 'entry':
            if self.currency in self.currencies:
                for date, rate in self.rates.items():
                    if self._check_date(date):
                        self.content[date.isoformat()][self.currency] = rate
            self.currency = None
            self.rates = None

        self.tags.pop()

    def _check_date(self, date):
        return (self.date_from is None or date >= self.date_from) and \
            (self.date_to is None or date <= self.date_to)
