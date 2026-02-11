# Copyright 2026 PT Solusi Aglis Indonesia (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Remove stale rate records for all companies' base currencies.

    When a company switches its base currency (e.g. from USD to IDR),
    historical rate records for the old foreign currency remain in
    res_currency_rate.  Odoo's company_rate formula divides the stored
    rate by the *last* rate found for the company's current base currency:

        company_rate = rate / last_base_currency_rate

    If last_base_currency_rate != 1.0 the displayed "Unit per IDR" /
    "IDR per Unit" columns become wildly incorrect, even though the raw
    Technical Rate is correct.

    This hook detects and removes any such stale records so the module
    works correctly on both fresh and migrated databases.
    """
    cr.execute(
        """
        SELECT rc.id, rc.name AS currency_name, COUNT(rcr.id) AS rate_count
        FROM res_company rco
        JOIN res_currency rc ON rc.id = rco.currency_id
        LEFT JOIN res_currency_rate rcr ON rcr.currency_id = rc.id
        GROUP BY rc.id, rc.name
        HAVING COUNT(rcr.id) > 0
        """
    )
    rows = cr.fetchall()
    if not rows:
        return

    for currency_id, currency_name, rate_count in rows:
        _logger.warning(
            "currency_rate_update_BI: Found %d stale rate record(s) for base "
            "currency '%s'. These cause incorrect company_rate display. "
            "Removing them now.",
            rate_count,
            currency_name,
        )
        cr.execute(
            "DELETE FROM res_currency_rate WHERE currency_id = %s",
            (currency_id,),
        )
        _logger.info(
            "currency_rate_update_BI: Removed %d rate record(s) for base "
            "currency '%s'.",
            rate_count,
            currency_name,
        )
