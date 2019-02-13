# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.rename_models(cr, {
        'currency.rate.update.service': 'res.currency.rate.provider',
    })
    openupgrade.rename_tables(cr, {
        'currency_rate_update_service': 'res_currency_rate_provider',
        'res_currency_auto_update_rel': '%(l)s_%(r)s_rel' % {
            'l': 'res_currency',
            'r': 'res_currency_rate_provider',
        },
    })
    openupgrade.rename_columns(cr, {
        '%(l)s_%(r)s_rel' % {
            'l': 'res_currency',
            'r': 'res_currency_rate_provider',
        }: [
            ('service_id', 'provider_id'),
        ],
    })
