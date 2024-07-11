# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    currency_old_rate_notify_days = fields.Integer(
        string="Warn when currency rates are older than",
        config_parameter="currency_old_rate_notify.max_days",
    )
