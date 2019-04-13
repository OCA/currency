# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    xe_com_account_id = fields.Char(
        string='Account ID',
        related='company_id.xe_com_account_id',
        readonly=False,
    )
    xe_com_account_api_key = fields.Char(
        string='API key',
        related='company_id.xe_com_account_api_key',
        readonly=False,
    )
