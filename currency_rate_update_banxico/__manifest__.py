# Copyright 2025 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Update: Banxico",
    "version": "17.0.1.0.0",
    "category": "Financial Management/Configuration",
    "summary": "Update exchange rates using Banxico",
    "author": "Jarsa, AMOdoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "currency_rate_update",
    ],
    "external_dependencies": {"python": ["requests-mock"]},
    "data": [
        "views/res_currency_rate_provider_views.xml",
    ],
}
