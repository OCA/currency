# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    transferwise_api_key = fields.Char(
        string='API Key',
        related='company_id.transferwise_api_key',
        readonly=False,
    )
