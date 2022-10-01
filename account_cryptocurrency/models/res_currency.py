# Copyright 2021 ForgeFlow S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models

_VALUATION_METHODS = [
    ("fifo", "First-in-First-Out"),
]


class ResCurrency(models.Model):
    _inherit = "res.currency"

    # We have to allow for 18 decimal places, which is what the maximum
    # Ethereum can be divided.
    rounding = fields.Float(digits=(12, 18))
    inventoried = fields.Boolean("Inventoried")
    valuation_method = fields.Selection(
        selection=_VALUATION_METHODS,
        string="Valuation Method",
    )
    inventory_account_id = fields.Many2one(
        "account.account",
        string="Inventory Account",
        company_dependent=True,
    )

    @api.constrains("inventory_account_id")
    def _check_inventory_account_id(self):
        for rec in self:
            if (
                rec.inventory_account_id
                and rec.inventory_account_id.currency_id
                and rec.inventory_account_id.currency_id.id != rec.id
            ):
                raise exceptions.ValidationError(
                    _("The currency of the Inventory Account should be %s") % rec.name
                )

    @api.constrains("inventoried", "valuation_method")
    def _check_currency_valuation_method(self):
        for rec in self:
            if rec.inventoried and not rec.valuation_method:
                raise exceptions.ValidationError(
                    _("You must indicate a valuation method for currency %s") % rec.name
                )
