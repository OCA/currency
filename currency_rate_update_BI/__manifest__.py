# Copyright 2026 PT Solusi Aglis Indonesia (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Update: Bank Indonesia",
    "version": "16.0.1.0.0",
    "category": "Financial Management/Configuration",
    "summary": "Update exchange rates using Bank Indonesia (BI) official rates",
    "author": "PT Solusi Aglis Indonesia, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["currency_rate_update"],
    "post_init_hook": "post_init_hook",
    "maintainers": ["hitrosol"],
}
