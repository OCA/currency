# Copyright 2026 LOYM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import date

import requests

from odoo import _, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCurrencyRateProvider(models.Model):
    _inherit = "res.currency.rate.provider"
    _frankfurter_url = "https://api.frankfurter.dev/v2/"

    service = fields.Selection(
        selection_add=[("frankfurter", "Frankfurter")],
        ondelete={"frankfurter": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "frankfurter":
            return super()._get_supported_currencies()
        return self._get_supported_currencies_frankfurter()

    def _get_supported_currencies_frankfurter(self):
        """Return currencies supported by the Frankfurter API."""
        try:
            return list(self._fetch_supported_currencies_frankfurter())
        except UserError:
            _logger.warning(
                "Couldn't fetch supported currencies from Frankfurter", exc_info=True
            )
            return []

    @tools.ormcache()
    def _fetch_supported_currencies_frankfurter(self):
        data = self._request_data_frankfurter(f"{self._frankfurter_url}currencies", {})
        return tuple(currency["iso_code"] for currency in data)

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "frankfurter":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        return self._get_rates_frankfurter(
            base_currency, currencies, date_from, date_to
        )

    def _get_rates_frankfurter(self, base_currency, currencies, date_from, date_to):
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

        url = f"{self._frankfurter_url}rates"
        data = self._request_data_frankfurter(url, params)
        result = {}
        for rate in data:
            rate_date = date.fromisoformat(rate["date"])
            result.setdefault(rate_date, {})
            result[rate_date][rate["quote"]] = rate["rate"]
        return result

    def _request_data_frankfurter(self, url, params):
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
                _(
                    "Couldn't fetch data from Frankfurter. "
                    "Please contact your administrator."
                )
            ) from error
