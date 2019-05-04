# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Currency Rate Update: TransferWise.com',
    'version': '12.0.1.0.0',
    'category': 'Financial Management/Configuration',
    'summary': 'Update exchange rates using TransferWise.com',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'depends': [
        'currency_rate_update',
    ],
    'data': [
        'views/res_config_settings.xml',
    ],
}
