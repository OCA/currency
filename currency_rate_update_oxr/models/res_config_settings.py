# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openexchangerates_app_id = fields.Char(
        string='App ID',
        related='company_id.openexchangerates_app_id',
        readonly=False,
    )
