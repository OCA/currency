# Copyright 2009-2016 Camptocamp
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    currency_rates_autoupdate = fields.Boolean(
        string="Automatic Currency Rates (OCA)",
        default=True,
        help="Enable automatic currency rates updates in this company.",
    )
