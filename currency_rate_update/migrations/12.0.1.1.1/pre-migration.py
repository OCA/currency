# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_field_renames = [
    ('res.company', 'res_company', 'auto_currency_up',
     'currency_rates_autoupdate'),
]

xmlid_renames = [
    ('currency_rate_update.currency_rate_update_service_multicompany_rule',
     'currency_rate_update.res_currency_rate_provider_multicompany'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
