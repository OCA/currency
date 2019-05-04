# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import timedelta
import dateutil.parser
import itertools
import json
import urllib.parse
import urllib.request

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderTransferWise(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('TransferWise', 'TransferWise.com')],
    )

    @api.multi
    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'TransferWise':
            return super()._get_supported_currencies()  # pragma: no cover

        url = 'https://api.transferwise.com/v1/rates'
        data = json.loads(self._transferwise_provider_retrieve(url))
        if 'error' in data and data['error']:
            raise UserError(
                data['error_description']
                if 'error_description' in data
                else 'Unknown error'
            )

        return list(set(itertools.chain.from_iterable(map(
            lambda entry: [entry['source'], entry['target']],
            data
        ))))

    @api.multi
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'TransferWise':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        content = defaultdict(dict)

        # NOTE: Step in 10 days is selected to reduce memory impact
        step = timedelta(days=10)
        for currency in currencies:
            since = date_from
            until = since + step
            while since <= date_to:
                url = (
                    'https://api.transferwise.com/v1/rates' +
                    '?from=%(from)s' +
                    '&to=%(to)s' +
                    '&source=%(source)s' +
                    '&target=%(target)s' +
                    '&group=day'
                ) % {
                    'source': base_currency,
                    'target': currency,
                    'from': str(since),
                    'to': str(min(until, date_to)),
                }
                data = json.loads(self._transferwise_provider_retrieve(url))
                if 'error' in data and data['error']:
                    raise UserError(
                        data['error_description']
                        if 'error_description' in data
                        else 'Unknown error'
                    )
                for entry in data:
                    date = dateutil.parser.parse(entry['time']).date()
                    date_content = content[date.isoformat()]
                    date_content[currency] = entry['rate']

                since += step
                until += step

        return content

    @api.multi
    def _transferwise_provider_retrieve(self, url):
        self.ensure_one()
        with self._transferwise_provider_urlopen(url) as response:
            content = response.read().decode(
                response.headers.get_content_charset()
            )
        return content

    @api.multi
    def _transferwise_provider_urlopen(self, url):
        self.ensure_one()

        if not self.company_id.transferwise_api_key:
            raise UserError(_(
                'No TransferWise.com credentials specified!'
            ))

        request = urllib.request.Request(url)
        request.add_header(
            'Authorization',
            'Bearer %s' % self.company_id.transferwise_api_key
        )
        return urllib.request.urlopen(request)
