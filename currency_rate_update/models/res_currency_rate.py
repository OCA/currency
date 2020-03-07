# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCurrencyRate(models.Model):
    _name = "res.currency.rate"
    _inherit = ["res.currency.rate", "mail.thread"]

    rate = fields.Float(track_visibility="onchange")
    provider_id = fields.Many2one(
        string="Provider",
        comodel_name="res.currency.rate.provider",
        ondelete="restrict",
        track_visibility="onchange",
    )

    def write(self, values):
        """Unset link to provider in case 'rate' or 'name' are manually changed
        """
        if ("rate" in values or "name" in values) and "provider_id" not in values:
            values["provider_id"] = False

        return super().write(values)
