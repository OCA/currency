# Copyright 2022 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (garazdcreation@gmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import dateutil.parser
import json
import logging
from collections import defaultdict
from typing import List

import requests
from requests.exceptions import Timeout, TooManyRedirects
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ResCurrencyRateProviderNBU(models.Model):
    """Implementation for National Bank of Ukraine"""

    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("NBU", "National Bank of Ukraine")],
        ondelete={"NBU": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "NBU":
            return super()._get_supported_currencies()
        # List of currencies obrained from:
        # https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json
        return [
            "AUD",
            "CAD",
            "CNY",
            "HRK",
            "CZK",
            "DKK",
            "HKD",
            "HUF",
            "INR",
            "IDR",
            "ILS",
            "JPY",
            "KZT",
            "KRW",
            "MXN",
            "MDL",
            "NZD",
            "NOK",
            "RUB",
            "SGD",
            "ZAR",
            "SEK",
            "CHF",
            "EGP",
            "GBP",
            "USD",
            "BYN",
            "AZN",
            "RON",
            "TRY",
            "XDR",
            "BGN",
            "EUR",
            "PLN",
            "DZD",
            "BDT",
            "AMD",
            "DOP",
            "IRR",
            "IQD",
            "KGS",
            "LBP",
            "LYD",
            "MYR",
            "MAD",
            "PKR",
            "SAR",
            "VND",
            "THB",
            "AED",
            "TND",
            "UZS",
            "TWD",
            "TMT",
            "RSD",
            "TJS",
            "GEL",
            "BRL",
            "XAU",
            "XAG",
            "XPT",
            "XPD",
        ]

    def _process_request(self, url, params=None, headers=None):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=60)
            response_data = json.loads(response.text)
            if response.status_code != 200:
                raise Exception(_("Failed to fetch from https://bank.gov.ua/ "
                                  "with error code: %s and error message: %s")
                                % (response.status_code, response.reason))
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            raise Exception(str(e))
        return response_data

    def _nbu_get_latest_rate(self, currencies: List, invert_calculation=True):
        """Get currency rates from NBU.
        :param currencies: list or currency codes to return
        :param invert_calculation: specify to invert a rate value or not
        :return: dict
        """
        content = defaultdict(dict)
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        data = self._process_request(url)
        for line in data:
            currency = line.get("cc")
            if currency in currencies:
                timestamp = fields.Date.to_string(
                    dateutil.parser.parse(line.get("exchangedate"),
                                          dayfirst=True))
                rate = float(line.get("rate", 0))
                if invert_calculation:
                    rate = 1.0 / rate
                content[timestamp].update({currency: rate})
        return content

    @api.model
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "NBU":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        if base_currency != self.env.ref('base.UAH').name:
            raise UserError(_('The base company currency should be "UAH" '
                              'to get NBU rates.'))
        if float_compare(
                self.env.ref('base.UAH').rate, 1.0, precision_digits=12) != 0:
            raise UserError(_('The base company currency rate should be '
                              'equal to 1.0'))
        return self._nbu_get_latest_rate(self.currency_ids.mapped('name'))
