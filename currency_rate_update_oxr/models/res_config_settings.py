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
    openexchangerates_eod_rates = fields.Boolean(
        string='End-of-day rates',
        related='company_id.openexchangerates_eod_rates',
        readonly=False,
        help='Yesterday\'s end-of-day rates will be used for today.',
    )
