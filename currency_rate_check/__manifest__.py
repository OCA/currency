# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Currency Rate Check',
    'version': '12.0.1.0.0',
    'author':
        'VanMoof, '
        'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/currency',
    'license': 'AGPL-3',
    'category': 'Financial Management/Configuration',
    'summary': 'Check exchange rates using OCA modules',
    'depends': [
        'currency_rate_update',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_line_currency_check.xml',
        'wizards/res_currency_rate_check_wizard.xml',
    ],
    'installable': True,
}
