# Copyright 2023 Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Currency Rate Update: Turkish Central Bank",
    "version": "16.0.1.1.0",
    "category": "Financial Management/Configuration",
    "summary": "Update exchange rates using TCMB.gov.tr",
    "author": "Yiğit Budak, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "currency_rate_update",
    ],
    "data": [
        "views/res_currency_rate_provider.xml",
    ],
}
