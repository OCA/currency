# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Cryptocurrency',
    'version': '11.0.1.0.0',
    'category': 'Account',
    'author': "Eficent,"
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/currency',
    'summary': 'Manage cryptocurrencies',
    "license": "AGPL-3",
    'depends': [
        "account",
    ],
    'data': [
        'security/account_cryptocurrency_security.xml',
        'security/ir.model.access.csv',
        'data/res_currency_move_sequence.xml',
        'views/res_currency_view.xml',
        'views/res_currency_move_menuitem.xml',
        'views/res_currency_move_view.xml',
        'views/res_currency_move_line_view.xml',
        'views/account_payment_view.xml',
    ],
}
