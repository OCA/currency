# Copyright 2026 AllRatesToday (https://allratestoday.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Update: AllRatesToday (official central-bank rates)",
    "version": "18.0.1.0.0",
    "category": "Financial Management/Configuration",
    "summary": "Update exchange rates from the table published by a central bank "
    "or tax authority (ECB, RBI, HMRC, CBK, ... 120+ publishers) via AllRatesToday",
    "author": "AllRatesToday, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["currency_rate_update"],
    "external_dependencies": {"python": ["requests"]},
    "data": ["views/res_currency_rate_provider.xml"],
}
