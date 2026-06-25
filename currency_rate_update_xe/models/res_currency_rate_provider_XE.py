# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
from datetime import date

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

# Public credentials embedded in xe.com's own front-end, required to reach its
# JSON converter endpoint.
XE_API_URL = "https://www.xe.com/api/protected/midmarket-converter/"
XE_API_TOKEN = base64.b64encode(b"lodestar:pugsnax").decode()


class ResCurrencyRateProviderXE(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("XE", "XE.com")],
        ondelete={"XE": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "XE":
            return super()._get_supported_currencies()
        # List of currencies obrained from: https://www.xe.com/currency/
        return [
            "USD",
            "EUR",
            "GBP",
            "CAD",
            "AUD",
            "JPY",
            "ADA",
            "AED",
            "AFN",
            "ALL",
            "AMD",
            "ANG",
            "AOA",
            "ARS",
            "AUD",
            "AWG",
            "AZN",
            "BAM",
            "BBD",
            "BCH",
            "BDT",
            "BGN",
            "BHD",
            "BIF",
            "BMD",
            "BND",
            "BOB",
            "BRL",
            "BSD",
            "BTC",
            "BTN",
            "BWP",
            "BYN",
            "BYR",
            "BZD",
            "CAD",
            "CDF",
            "CHF",
            "CLP",
            "CNY",
            "COP",
            "CRC",
            "CUC",
            "CUP",
            "CVE",
            "CZK",
            "DJF",
            "DKK",
            "DOGE",
            "DOP",
            "DOT",
            "DZD",
            "EEK",
            "EGP",
            "ERN",
            "ETB",
            "ETH",
            "EUR",
            "FJD",
            "FKP",
            "GBP",
            "GEL",
            "GGP",
            "GHS",
            "GIP",
            "GMD",
            "GNF",
            "GTQ",
            "GYD",
            "HKD",
            "HNL",
            "HRK",
            "HTG",
            "HUF",
            "IDR",
            "ILS",
            "IMP",
            "INR",
            "IQD",
            "IRR",
            "ISK",
            "JEP",
            "JMD",
            "JOD",
            "JPY",
            "KES",
            "KGS",
            "KHR",
            "KMF",
            "KPW",
            "KRW",
            "KWD",
            "KYD",
            "KZT",
            "LAK",
            "LBP",
            "LINK",
            "LKR",
            "LRD",
            "LSL",
            "LTC",
            "LTL",
            "LUNA",
            "LVL",
            "LYD",
            "MAD",
            "MDL",
            "MGA",
            "MKD",
            "MMK",
            "MNT",
            "MOP",
            "MRU",
            "MUR",
            "MVR",
            "MWK",
            "MXN",
            "MYR",
            "MZN",
            "NAD",
            "NGN",
            "NIO",
            "NOK",
            "NPR",
            "NZD",
            "OMR",
            "PAB",
            "PEN",
            "PGK",
            "PHP",
            "PKR",
            "PLN",
            "PYG",
            "QAR",
            "RON",
            "RSD",
            "RUB",
            "RWF",
            "SAR",
            "SBD",
            "SCR",
            "SDG",
            "SEK",
            "SGD",
            "SHP",
            "SLE",
            "SLL",
            "SOS",
            "SPL",
            "SRD",
            "STN",
            "SVC",
            "SYP",
            "SZL",
            "THB",
            "TJS",
            "TMT",
            "TND",
            "TOP",
            "TRY",
            "TTD",
            "TVD",
            "TWD",
            "TZS",
            "UAH",
            "UGX",
            "UNI",
            "USD",
            "UYU",
            "UZS",
            "VEF",
            "VES",
            "VND",
            "VUV",
            "WST",
            "XAF",
            "XAG",
            "XAU",
            "XCD",
            "XDR",
            "XLM",
            "XOF",
            "XPD",
            "XPF",
            "XPT",
            "XRP",
            "YER",
            "ZAR",
            "ZMK",
            "ZMW",
            "ZWD",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "XE":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        # XE.com blocks automated requests to its public HTML pages
        # (CloudFront answers 403 regardless of the User-Agent sent), so we
        # read the JSON endpoint that powers xe.com's own converter instead.
        # That endpoint only exposes the latest mid-market rates, hence we
        # always return today's rates regardless of the requested range.
        api_rates = self._get_xe_rates()
        base_rate = api_rates.get(base_currency)
        if not base_rate:
            raise UserError(
                _("XE.com didn't return a rate for the base currency %s.")
                % base_currency
            )
        rates = {}
        for currency in currencies:
            if currency == base_currency:
                continue
            rate = api_rates.get(currency)
            if rate:
                # API rates are USD-based; make them relative to base_currency.
                rates[currency] = rate / base_rate
        return {date.today(): rates}

    def _get_xe_rates(self):
        """Return the latest mid-market rates (USD-based) from XE.com."""
        try:
            response = requests.get(
                XE_API_URL,
                timeout=30,
                headers={
                    "Authorization": "Basic %s" % XE_API_TOKEN,
                    "User-Agent": "Mozilla/5.0",
                },
            )
            response.raise_for_status()
        except Exception as e:
            raise UserError(
                _("Couldn't fetch data. Please contact your administrator.")
            ) from e
        return response.json().get("rates", {})
