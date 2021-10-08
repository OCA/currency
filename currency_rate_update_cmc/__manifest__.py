# Copyright 2021 ForgeFlow S.L.
# Copyright 2018 Fork Sand Inc.
# Copyright 2018 Ross Golder
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Update Coin Market Cap",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Allows to download crypto currency exchange rates from "
    "Coin Market Cap",
    "author": "ForgeFlow S.L.," "Odoo Community Association (OCA),",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "depends": [
        "currency_rate_update",
    ],
    "data": [
        "wizards/res_currency_rate_update_wizard.xml",
    ],
    "installable": True,
}
