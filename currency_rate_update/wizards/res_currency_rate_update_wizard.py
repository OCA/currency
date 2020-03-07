# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCurrencyRateUpdateWizard(models.TransientModel):
    _name = "res.currency.rate.update.wizard"
    _description = "Currency Rate Update Wizard"

    date_from = fields.Date(
        string="Start Date", required=True, default=fields.Date.context_today
    )
    date_to = fields.Date(
        string="End Date", required=True, default=fields.Date.context_today
    )
    provider_ids = fields.Many2many(
        string="Providers",
        comodel_name="res.currency.rate.provider",
        column1="wizard_id",
        column2="provider_id",
    )

    def action_update(self):
        self.ensure_one()

        self.provider_ids._update(self.date_from, self.date_to)

        return {"type": "ir.actions.act_window_close"}
