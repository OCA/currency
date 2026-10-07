# Copyright 2026 LOYM

# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

import requests

from odoo import fields, models
from odoo.exceptions import UserError


class ResCurrencyRateProviderFrankfurter(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("Frankfurter", "Frankfurter")],
        ondelete={"Frankfurter": "set default"},
    )

    def _get_supported_currencies(self):
        """Return currencies supported by the Frankfurter API."""
        response = requests.get(
            "https://api.frankfurter.dev/v2/currencies",
            timeout=10,
        )
        response.raise_for_status()
        currencies = [currency["iso_code"] for currency in response.json()]
        return currencies

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()

        if self.service != "Frankfurter":
            return super()._obtain_rates(
                base_currency,
                currencies,
                date_from,
                date_to,
            )

        return self._get_rates(
            base_currency,
            currencies,
            date_from,
            date_to,
        )

    def _get_rates(
        self,
        base_currency,
        currencies,
        date_from,
        date_to,
    ):
        """Get exchange rates from Frankfurter."""

        currency_codes = [
            currency for currency in currencies if currency != base_currency
        ]

        if not currency_codes:
            return {}

        params = {
            "base": base_currency,
            "quotes": ",".join(currency_codes),
        }

        if date_from == date_to:
            params["date"] = date_from.isoformat()
        else:
            params["from"] = date_from.isoformat()
            params["to"] = date_to.isoformat()

        url = "https://api.frankfurter.dev/v2/rates"

        data = self._request_data(url, params)

        result = {}

        for rate in data:
            rate_date = date.fromisoformat(rate["date"])
            result.setdefault(rate_date, {})
            result[rate_date][rate["quote"]] = rate["rate"]

        return result

    def _request_data(self, url, params):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as error:
            raise UserError(
                self.env._(
                    "Couldn't fetch data from Frankfurter. "
                    "Please contact your administrator."
                )
            ) from error
