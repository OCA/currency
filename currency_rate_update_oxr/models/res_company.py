# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    openexchangerates_app_id = fields.Char(
        string='OpenExchangeRates.org App ID',
    )
    openexchangerates_eod_rates = fields.Boolean(
        string='End-of-day rates',
        help='Yesterday\'s end-of-day rates will be used for today.',
    )
