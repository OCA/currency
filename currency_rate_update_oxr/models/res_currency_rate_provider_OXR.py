# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import timedelta
import json
import urllib.parse
import urllib.request

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderOXR(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('OXR', 'OpenExchangeRates.org')],
    )

    @api.multi
    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'OXR':
            return super()._get_supported_currencies()  # pragma: no cover

        url = 'https://openexchangerates.org/api/currencies.json'
        data = json.loads(self._oxr_provider_retrieve(url))
        if 'error' in data and data['error']:
            raise UserError(
                data['description']
                if 'description' in data
                else 'Unknown error'
            )

        return list(data.keys())

    @api.multi
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'OXR':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        content = defaultdict(dict)

        date = date_from
        while date <= date_to:
            url = (
                'https://openexchangerates.org/api/historical' +
                '/%(date)s.json'
                '?base=%(from)s' +
                '&symbols=%(to)s'
            ) % {
                'from': base_currency,
                'to': ','.join(currencies),
                'date': str(date),
            }
            data = json.loads(self._oxr_provider_retrieve(url))
            if 'error' in data and data['error']:
                raise UserError(
                    data['description']
                    if 'description' in data
                    else 'Unknown error'
                )
            date_content = content[date.isoformat()]
            if 'rates' in data:
                for currency, rate in data['rates'].items():
                    date_content[currency] = rate

            date += timedelta(days=1)

        return content

    @api.multi
    def _oxr_provider_retrieve(self, url):
        self.ensure_one()
        with self._oxr_provider_urlopen(url) as response:
            content = response.read().decode(
                response.headers.get_content_charset()
            )
        return content

    @api.multi
    def _oxr_provider_urlopen(self, url):
        self.ensure_one()

        if not self.company_id.openexchangerates_app_id:
            raise UserError(_(
                'No OpenExchangeRates.org credentials specified!'
            ))

        parsed_url = urllib.parse.urlparse(url)
        parsed_query = urllib.parse.parse_qs(parsed_url.query)
        parsed_query['app_id'] = self.company_id.openexchangerates_app_id
        parsed_url = parsed_url._replace(query=urllib.parse.urlencode(
            parsed_query,
            doseq=True,
            quote_via=urllib.parse.quote,
        ))
        url = urllib.parse.urlunparse(parsed_url)

        request = urllib.request.Request(url)
        request.add_header(
            'Authorization',
            'Token %s' % self.company_id.openexchangerates_app_id
        )
        return urllib.request.urlopen(request)
