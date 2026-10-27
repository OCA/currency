# Copyright 2026 AllRatesToday (https://allratestoday.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import re
from datetime import date, timedelta

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

from ..tools import per_pivot, rebase

BASE_URL = "https://allratestoday.com"
BANK_CODE_RE = re.compile(r"^[a-z0-9_]{2,32}$")
MAX_HISTORY_DAYS = 400


class ResCurrencyRateProviderAllRatesToday(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[
            ("AllRatesToday", "AllRatesToday (official central-bank rates)")
        ],
        ondelete={"AllRatesToday": "set default"},
    )
    allratestoday_bank = fields.Char(
        string="Publisher code",
        default="ecb",
        help="Short code of the central bank or tax authority whose published "
        "table must be used, e.g. ecb, rbi, hmrc, cbk. The full list is at "
        "https://allratestoday.com/central-bank-rates-api/institutions/",
    )
    allratestoday_api_key = fields.Char(
        string="AllRatesToday API key",
        help="Optional. Without a key the latest table is fetched from the "
        "keyless open endpoint. Past dates (the wizard with a date range) need "
        "a key on a paid plan. Keys: https://allratestoday.com/register",
    )
    allratestoday_rate_type = fields.Char(
        string="Rate type",
        help="Optional. Pin one of the publisher's series when it prints several "
        "for the same pair (e.g. buy, sell, middle, reference). Leave empty to "
        "take the most general series available.",
    )

    # -- helpers ---------------------------------------------------------

    def _allratestoday_bank_code(self):
        self.ensure_one()
        bank = (self.allratestoday_bank or "ecb").strip().lower()
        if not BANK_CODE_RE.match(bank):
            raise UserError(
                _(
                    "AllRatesToday publisher code %s is not valid. Use the short "
                    "code from https://allratestoday.com/central-bank-rates-api/"
                    "institutions/ (for example ecb, rbi, hmrc).",
                    bank,
                )
            )
        return bank

    def _allratestoday_get(self, path):
        """GET one table. Returns the parsed JSON ``{"rate_date", "rates", ...}``
        or ``None`` for a 404 (no table on that date)."""
        self.ensure_one()
        headers = {
            "Accept": "application/json",
            "User-Agent": "odoo-currency_rate_update_allratestoday/18.0",
        }
        key = (self.allratestoday_api_key or "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        try:
            response = requests.get(BASE_URL + path, headers=headers, timeout=30)
        except requests.RequestException as e:
            raise UserError(_("Could not reach AllRatesToday: %s", e)) from e
        if response.status_code == 404:
            return None
        if response.status_code == 401:
            raise UserError(
                _(
                    "AllRatesToday rejected the API key. Check it on the provider "
                    "or create a free key at https://allratestoday.com/register"
                )
            )
        if response.status_code == 403:
            raise UserError(
                _(
                    "The AllRatesToday plan on this key does not include this "
                    "request (dated tables need a paid plan): %s",
                    response.text[:300],
                )
            )
        if response.status_code != 200:
            raise UserError(
                _(
                    "AllRatesToday returned HTTP %s. Contact your administrator.",
                    response.status_code,
                )
            )
        try:
            data = response.json()
        except ValueError as e:
            raise UserError(_("AllRatesToday returned a non-JSON response.")) from e
        if not isinstance(data.get("rates"), list) or not data.get("rate_date"):
            raise UserError(_("Unexpected AllRatesToday response shape."))
        return data

    def _allratestoday_latest(self, bank):
        if (self.allratestoday_api_key or "").strip():
            return self._allratestoday_get(f"/api/v1/central-bank/{bank}/latest")
        return self._allratestoday_get(f"/api/open/central-bank/{bank}")

    def _allratestoday_table_to_rates(self, table, base_currency, currencies):
        per_piv = per_pivot(
            table["rates"],
            rate_type=(self.allratestoday_rate_type or "").strip().lower() or None,
            preferred_pivots=[base_currency],
        )
        if base_currency not in per_piv:
            raise UserError(
                _(
                    "The %(bank)s table for %(date)s does not quote %(ccy)s, so it "
                    "cannot be rebased to the company currency.",
                    bank=self.allratestoday_bank,
                    date=table["rate_date"],
                    ccy=base_currency,
                )
            )
        return rebase(per_piv, base_currency, currencies)

    # -- provider contract ----------------------------------------------

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "AllRatesToday":
            return super()._get_supported_currencies()  # pragma: no cover
        table = self._allratestoday_latest(self._allratestoday_bank_code())
        if not table:
            return []
        codes = set()
        for row in table["rates"]:
            codes.add(row["base"])
            codes.add(row["quote"])
        return sorted(codes)

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "AllRatesToday":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover
        bank = self._allratestoday_bank_code()
        currencies = set(currencies)
        content = {}

        latest = self._allratestoday_latest(bank)
        if not latest:
            raise UserError(
                _("AllRatesToday has no published table for publisher code %s.", bank)
            )
        latest_date = fields.Date.from_string(latest["rate_date"])
        if date_from <= latest_date <= date_to:
            content[latest["rate_date"]] = self._allratestoday_table_to_rates(
                latest, base_currency, currencies
            )

        # Dates before the latest table come from the dated endpoint, one call
        # per day. It answers with the newest table on or before the requested
        # day, so the result is keyed by the date it actually carries.
        history_to = min(date_to, latest_date - timedelta(days=1), date.today())
        if date_from <= history_to:
            if not (self.allratestoday_api_key or "").strip():
                raise UserError(
                    _(
                        "Past dates need an AllRatesToday API key on a paid plan. "
                        "Without a key only the latest published table is available."
                    )
                )
            if (history_to - date_from).days > MAX_HISTORY_DAYS:
                raise UserError(
                    _(
                        "Date range too long: at most %s days per update.",
                        MAX_HISTORY_DAYS,
                    )
                )
            seen = set(content)
            current = history_to
            while current >= date_from:
                table = self._allratestoday_get(
                    f"/api/v1/central-bank/{bank}/{current.isoformat()}"
                )
                if (
                    table
                    and table["rate_date"] not in seen
                    and fields.Date.from_string(table["rate_date"]) >= date_from
                ):
                    seen.add(table["rate_date"])
                    content[table["rate_date"]] = self._allratestoday_table_to_rates(
                        table, base_currency, currencies
                    )
                    # Jump back to the day before the table we just got.
                    current = fields.Date.from_string(table["rate_date"])
                current -= timedelta(days=1)
        return content
