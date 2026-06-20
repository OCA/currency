# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# Copyright 2026 Altixia (https://altixia.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import itertools
import logging
import re
from collections import defaultdict
from datetime import date, timedelta

import dateutil.parser
import requests

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

WISE_API_URL = "https://api.wise.com/v1/rates"
# Network timeout (connect, read) in seconds: a scheduled cron must never hang
# indefinitely on an unresponsive endpoint.
TIMEOUT = (10, 30)
# Legacy UUID token format. Wise is migrating API tokens to JWT; a UUID token
# is still valid today but should eventually be regenerated as JWT.
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
# Warn only during the migration window. Wise starts issuing JWT tokens in
# production with the transition period beginning end of July 2026, so warning
# before then is not actionable (UUID is the only available format). A year
# later the migration is over, so we stop the check to avoid nagging for years.
_LEGACY_WARN_FROM = date(2026, 8, 1)
_LEGACY_WARN_UNTIL = date(2027, 8, 1)


class ResCurrencyRateProviderWise(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("Wise", "Wise.com")],
        ondelete={"Wise": "set default"},
    )

    def _register_hook(self):
        # Emit the legacy-token warning at Odoo load time.
        res = super()._register_hook()
        self.search([("service", "=", "Wise")])._wise_warn_legacy_tokens()
        return res

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "Wise":
            return super()._get_supported_currencies()  # pragma: no cover

        data = self._wise_provider_retrieve(WISE_API_URL)
        self._wise_check_error(data)

        return list(
            set(
                itertools.chain.from_iterable(
                    [entry["source"], entry["target"]] for entry in data
                )
            )
        )

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "Wise":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover

        # Also warn on each scheduled update run (once per run).
        self._wise_warn_legacy_tokens()
        content = defaultdict(dict)

        # NOTE: Step in 10 days is selected to reduce memory impact
        step = timedelta(days=10)
        for currency in currencies:
            since = date_from
            until = since + step
            while since <= date_to:
                params = {
                    "source": base_currency,
                    "target": currency,
                    "from": str(since),
                    "to": str(min(until, date_to)),
                    "group": "day",
                }
                data = self._wise_provider_retrieve(WISE_API_URL, params)
                self._wise_check_error(data)
                for entry in data:
                    date = dateutil.parser.parse(entry["time"]).date()
                    date_content = content[date.isoformat()]
                    date_content[currency] = entry["rate"]

                since += step
                until += step

        return content

    def _wise_warn_legacy_tokens(self):
        """Warn for each Wise provider whose token still uses the UUID format.

        Wise is migrating API tokens from the legacy UUID format to JWT. A UUID
        token is still valid today but should eventually be regenerated as JWT
        in the Wise Developer Hub. Nothing is logged when no key is set, and the
        token storage already accepts both formats.
        """
        today = fields.Date.today()
        if not (_LEGACY_WARN_FROM <= today < _LEGACY_WARN_UNTIL):
            return
        for provider in self:
            key = provider.company_id.wise_api_key
            if key and _UUID_RE.match(key):
                _logger.warning(
                    "Wise.com API key for company %s is a legacy UUID-format "
                    "token. Wise is migrating API tokens to JWT; consider "
                    "regenerating the token in the Wise Developer Hub.",
                    provider.company_id.name,
                )

    def _wise_check_error(self, data):
        """Raise a clear error if the API returned an error payload."""
        if isinstance(data, dict) and data.get("error"):
            raise UserError(
                data.get("error_description") or self.env._("Unknown error")
            )

    def _wise_provider_retrieve(self, url, params=None):
        self.ensure_one()
        if not self.company_id.wise_api_key:
            raise UserError(self.env._("No Wise.com credentials specified!"))

        try:
            response = requests.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {self.company_id.wise_api_key}"},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            raise
        except requests.exceptions.RequestException as e:
            raise UserError(self.env._("Could not reach Wise.com: %s", e)) from e
        except ValueError as e:  # invalid JSON
            raise UserError(
                self.env._("Unexpected (non-JSON) response from Wise.com")
            ) from e
