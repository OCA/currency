# -*- coding: utf-8 -*-
{
    "name": "res_currency_rate_provider_BCV",

    "summary": """OCA version for BCV scrapping rates
       """,

    "author": "Luis Pinzón, Odoo Community Association (OCA)",
    "website": "https://www.linkedin.com/in/luis-a-pinz%C3%B3n-38103911/",
    "license": "AGPL-3",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Financial Management/Configuration",
    "version": "16.0.1.1.2",

    # any module necessary for this one to work correctly
    "depends": ["currency_rate_update"],

    # always loaded
    "data": [
        "views/views.xml",
    ],

}
