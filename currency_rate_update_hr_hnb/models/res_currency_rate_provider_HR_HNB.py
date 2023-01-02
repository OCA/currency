# Copyright 2023 DAJ MI 5
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging
import json
import urllib.request as request
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class ResCurrencyRateProviderHrHNB(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('HR-HNB', 'Croatia-HNB')],
        ondelete={"HR-HNB": "set default"},
    )

    # def _create_company_currency_rate(self):
    #     rcr = self.env['res.currency.rate']
    #     cc_provider_rate = rcr.search(
    #         [('provider_id', '=', self.id),
    #          ('company_id', '=', self.company_id.id),
    #          ('currency_id', '=', self.company_id.currency_id.id)])
    #     if not cc_provider_rate:
    #         rcr.create({
    #             'name': fields.Date.from_string('2000-01-01'),
    #             'rate': 1,
    #             'currency_id': self.company_id.currency_id.id,
    #             'company_id': self.company_id.id,
    #             'provider_id': self.id
    #         })
    #     return True

    # @api.multi
    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'HR-HNB':
            return super()._get_supported_currencies()  # pragma: no cover

        data = self._l10n_hr_hnb_urlopen()
        currencies = [c['valuta'] for c in data]
        # BOLE: ovo paziti jer moguce je da bas na taj dan nemam
        # sve valute.. ali very low impact pa se ne mucim oko ovog
        return currencies

    # @api.multi
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        # self._create_company_currency_rate()
        if self.service != 'HR-HNB':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        result = {}
        currencies = [c.name for c in self.currency_ids]
        data = self._l10n_hr_hnb_urlopen(
            currencies=currencies,
            date_from=date_from, date_to=date_to)
        for cd in data:
            currency = cd['valuta']
            if currency not in currencies:
                continue
            rate_date = cd['datum_primjene']
            # there is 3 rates: buy, mid, sell,
            # legaly required is to post all moves using mid rate, so no config on this part
            rate = cd.get('srednji_tecaj').replace(',', '.')
            try:
                rate = float(rate)
            except:
                _logger.debug("HNB problem rate not float: ", str(cd))
                continue
            # not directly dependant but have in mind
            if not result.get(rate_date):
                result[rate_date] = {currency: rate}
            else:
                result[rate_date].update({currency: rate})
        return result


    # @api.multi
    def _l10n_hr_hnb_urlopen(self, currencies=None, date_from=None, date_to=None):
        url = "https://api.hnb.hr/tecajn-eur/v3"
        if date_from is not None:
            if date_to is not None:
                url += "?datum-primjene-od=%s&datum-primjene-do=%s" % (
                    fields.Date.to_string(date_from),
                    fields.Date.to_string(date_to)
                )
        if currencies is not None:
            cur = '&'.join(['valuta=' + c for c in currencies])
            url += "?" + cur

        res = request.urlopen(url)
        data = json.loads(res.read().decode("UTF-8"))
        return data

