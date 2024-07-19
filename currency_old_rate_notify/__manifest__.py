# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Currency Old Rate Notify",
    "version": "16.0.1.1.0",
    "category": "Accounting",
    "license": "AGPL-3",
    "summary": "Notify accounting managers when currency rates are too old",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/currency",
    "depends": ["account", "web_notify"],
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "wizards/res_config_settings.xml",
    ],
}
