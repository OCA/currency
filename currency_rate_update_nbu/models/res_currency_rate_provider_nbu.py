# Copyright 2022 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<garazdcreation@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import json
import logging
from collections import defaultdict

import requests
from requests.exceptions import Timeout, TooManyRedirects

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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
            "USD",
            "EUR",
        ]

    def _process_request(self, url, params, headers):
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=60)
            response_data = json.loads(response.text)
            status = response_data.get("status")
            if status and status.get("error_code", False):
                raise Exception(
                    _(
                        "Failed to fetch from https://bank.gov.ua/ with error"
                        " code: %s and error message: %s"
                    )
                    % (status.get("error_code"), status.get("error_message"))
                )
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            raise Exception(str(e))
        return response_data

    def _get_latest_rate(self, currencies, base_currency, headers):
        content = defaultdict(dict)
        url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        params = {}
        data = self._process_request(url, params, headers)
        for line in data:
            timestamp = line.get("exchangedate")
            content[timestamp].update({line.get("cc"): line.get("rate", 0)})
        return content

    # def _get_historical_rate(
    #     self, currencies, date_from, date_to, base_currency, headers
    # ):
    #     content = defaultdict(dict)
    #     url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/historical"
    #     params = {
    #         "symbol": ",".join(currencies),
    #         "time_start": date_from,
    #         "time_end": date_to,
    #         "interval": "1d",
    #         "convert": base_currency,
    #     }
    #     data = self._process_request(url, params, headers)
    #     for currency, vals in data.items():
    #         for quote in vals.get("quotes", {}):
    #             timestamp = quote.get("timestamp")[:10]
    #             convert_currency = quote.get("quote", {}).get(base_currency, {})
    #             if convert_currency:
    #                 rate = convert_currency.get("price", 0)
    #                 content[timestamp].update({currency: rate})
    #     return content

    # @api.model
    # def _obtain_rates(self, base_currency, currencies, date_from, date_to):
    #     self.ensure_one()
    #     if "CMC" not in self.service:
    #         return super()._obtain_rates(base_currency, currencies, date_from, date_to)
    #     if base_currency not in ALLOWED_BASE_CURRENCIES:
    #         raise UserError(
    #             _("Company currency %s is not allowed in " "CoinMarketCap service ")
    #             % base_currency
    #         )
    #     if base_currency in currencies:
    #         currencies.remove(base_currency)
    #
    #     API_KEY = self.env["ir.config_parameter"].get_param("X-CMC_PRO_API_KEY")
    #     if not API_KEY:
    #         raise UserError(
    #             _(
    #                 "API KEY not found in System Parameters. Make sure to "
    #                 "define the API KEY using the key X-CMC_PRO_API_KEY"
    #             )
    #         )
    #     headers = {
    #         "Accepts": "application/json",
    #         "X-CMC_PRO_API_KEY": API_KEY,
    #     }
    #
    #     if self.service == "CMC Standard":
    #         return self._get_historical_rate(
    #             currencies, date_from, date_to, base_currency, headers
    #         )
    #     else:
    #         return self._get_latest_rate(currencies, base_currency, headers)

    @api.model
    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "NBU":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        if base_currency in currencies:
            currencies.remove(base_currency)
        return self._get_latest_rate(currencies, base_currency, headers)
