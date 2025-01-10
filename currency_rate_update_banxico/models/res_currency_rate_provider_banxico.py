# Copyright 2025 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError


class ResCurrencyRateProvider(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("banxico", "Bank of Mexico")],
        ondelete={"banxico": "set default"},
    )
    banxico_token = fields.Char()

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "banxico":
            return super()._get_supported_currencies()
        return ["EUR", "CAD", "JPY", "GBP", "USD"]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        """Get the exchange rates from the provider."""
        self.ensure_one()
        if self.service != "banxico":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        result = {}
        for currency in currencies:
            url = self._get_banxico_webservice_url(currency, date_from, date_to)
            data = self._request_data(url)
            result.update(self._process_data(data, currency))
        return result

    def _get_banxico_webservice_url(self, currency, date_from, date_to):
        """Get the URL to request the exchange rates"""
        base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/"
        currencies_map = {
            "EUR": "SF46410",
            "CAD": "SF60632",
            "GBP": "SF46407",
            "JPY": "SF46406",
            "USD": "SF60653",
        }
        if date_from < fields.Date.context_today(self):
            return (
                f"{base_url}{currencies_map[currency]}/datos/"
                "{date_from.strftime('%Y-%m-%d')}/{date_to.strftime('%Y-%m-%d')}"
            )
        return f"{base_url}{currencies_map[currency]}/datos/oportuno"

    def _request_data(self, url):
        try:
            headers = {
                "Bmx-Token": self.banxico_token,
            }
            response = requests.request("GET", url, headers=headers, timeout=10)
            if response.status_code != 200:
                raise UserError(
                    response.json()
                    .get("error", {})
                    .get(
                        "mensaje",
                        _("Couldn't fetch data. Please contact your administrator."),
                    )
                )
            return response.json()
        except Exception as e:
            raise UserError(
                _("Couldn't fetch data. Please contact your administrator.")
            ) from e

    def _process_data(self, data, currency):
        result = {}
        records = data.get("bmx", {}).get("series", [{}])[0].get("datos", [])
        for rec in records:
            date = datetime.strptime(rec.get("fecha"), "%d/%m/%Y")
            result[date] = {currency: 1 / float(rec["dato"])}
        return result
