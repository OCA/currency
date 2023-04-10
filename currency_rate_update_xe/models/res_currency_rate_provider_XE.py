# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date, timedelta

import requests
from lxml import etree

from odoo import _, fields, models
from odoo.exceptions import UserError


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
        base_url = "http://www.xe.com/currencytables"
        if date_from < date.today():
            return self._get_historical_rate(
                base_url, currencies, date_from, date_to, base_currency
            )
        else:
            return self._get_latest_rate(base_url, currencies, base_currency)

    def _get_latest_rate(self, base_url, currencies, base_currency):
        """Get all the exchange rates for today"""
        url = f"{base_url}/?from={base_currency}"
        data = self._request_data(url)
        return {date.today(): self._parse_data(data, currencies)}

    def _get_historical_rate(
        self, base_url, currencies, date_from, date_to, base_currency
    ):
        """Get all the exchange rates from 'date_from' to 'date_to'"""
        content = {}
        current_date = date_from
        while current_date <= date_to:
            url = f"{base_url}/?from={base_currency}&date={current_date.strftime('%Y-%m-%d')}"
            data = self._request_data(url)
            content[current_date] = self._parse_data(data, currencies)
            current_date += timedelta(days=1)
        return content

    def _request_data(
        self,
        url,
    ):
        try:
            return requests.request("GET", url)
        except Exception as e:
            raise UserError(
                _("Couldn't fetch data. Please contact your administrator.")
            ) from e

    def _parse_data(self, data, currencies):
        result = {}
        html_elem = etree.fromstring(data.content, etree.HTMLParser())
        rows_elem = html_elem.xpath(".//div[@id='table-section']//tbody/tr")
        for row_elem in rows_elem:
            currency_code = "".join(row_elem.find(".//th").itertext()).strip()
            if currency_code in currencies:
                rate = float(row_elem.find("td[2]").text.replace(",", ""))
                result[currency_code] = rate
        return result
