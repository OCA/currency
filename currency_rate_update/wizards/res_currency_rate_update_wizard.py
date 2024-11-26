# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


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

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self._context.get(
            "active_model"
        ) == "res.currency.rate.provider" and self._context.get("active_ids"):
            res["provider_ids"] = [Command.set(self._context["active_ids"])]
        return res

    def action_update(self):
        self.ensure_one()
        self.provider_ids._update(self.date_from, self.date_to)
