# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Currency Monthly Rate",
    "version": "12.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic Modules/Accounting",
    "website": "https://github.com/OCA/currency",
    "depends": ['base'],
    "data": [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/res_currency.xml',
    ],
    'installable': True,
}
