# Copyright 2026 Altixia (https://altixia.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Rename currency_rate_update_transferwise -> _wise (Wise rebrand, 2021).

    Preserves provider records, the API key and the rate history
    (kept in core res_currency_rate). No data loss.
    """
    if openupgrade.is_module_installed(env.cr, "currency_rate_update_transferwise"):
        openupgrade.update_module_names(
            env.cr,
            [("currency_rate_update_transferwise", "currency_rate_update_wise")],
            merge_modules=True,
        )
    if openupgrade.column_exists(env.cr, "res_company", "transferwise_api_key"):
        openupgrade.rename_columns(
            env.cr, {"res_company": [("transferwise_api_key", "wise_api_key")]}
        )
    openupgrade.logged_query(
        env.cr,
        "UPDATE res_currency_rate_provider SET service = 'Wise' "
        "WHERE service = 'TransferWise'",
    )
