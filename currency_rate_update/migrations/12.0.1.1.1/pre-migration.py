# Copyright 2019 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_column_renames = {
    'res_currency_auto_update_rel': [('service_id', 'provider_id')]
}

_field_renames = [
    ('res.company', 'res_company', 'auto_currency_up',
     'currency_rates_autoupdate'),
    ('currency.rate.update.service', 'currency_rate_update_service',
     'currency_list', 'available_currency_ids'),
    ('currency.rate.update.service', 'currency_rate_update_service',
     'currency_to_update', 'currency_ids'),
]

_model_renames = [
    ('currency.rate.update.service', 'res.currency.rate.provider'),
]

_table_renames = [
    ('currency_rate_update_service', 'res_currency_rate_provider'),
    ('res_currency_auto_update_rel', 'res_currency_res_currency_rate_provider_rel'),
]

xmlid_renames = [
    ('currency_rate_update.currency_rate_update_service_multicompany_rule',
     'currency_rate_update.res_currency_rate_provider_multicompany'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    openupgrade.rename_fields(env, _field_renames)
    openupgrade.rename_models(env.cr, _model_renames)
    openupgrade.rename_tables(env.cr, _table_renames)
    openupgrade.rename_xmlids(env.cr, xmlid_renames)
