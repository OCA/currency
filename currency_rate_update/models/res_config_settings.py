# Copyright 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_rates_autoupdate = fields.Boolean(
        string='Automatic Currency Rates (OCA)',
        related='company_id.currency_rates_autoupdate',
        readonly=False,
        help='Enable regular automatic currency rates updates',
    )
