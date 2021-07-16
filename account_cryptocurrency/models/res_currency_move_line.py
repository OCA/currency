# Copyright 2021 ForgeFlow S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [("draft", "Draft"), ("posted", "Posted"), ("cancel", "Cancelled")]

_DIRECTIONS = [
    ("inbound", "Receive Money"),
    ("outbound", "Send Money"),
]


class ResCurrencyMoveLine(models.Model):
    _name = "res.currency.move.line"
    _description = "Currency Move Line"

    move_id = fields.Many2one(
        "res.currency.move",
        string="Currency Move",
        ondelete="cascade",
        required="True",
        readonly=True,
    )
    date = fields.Date(
        string="Payment Date",
        default=fields.Date.context_today,
        required=True,
        copy=False,
        readonly=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="move_id.company_id",
        store=True,
    )
    company_currency = fields.Many2one(
        "res.currency",
        string="Company currency",
        related="company_id.currency_id",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="move_id.currency_id",
        store=True,
    )
    direction = fields.Selection(
        string="Direction",
        related="move_id.direction",
        store=True,
    )
    quantity = fields.Float(
        "Quantity",
        readonly=True,
    )
    amount = fields.Float(
        "Amount",
        help="Amount in company currency",
        readonly=True,
    )
    price_unit = fields.Float(
        "Price Unit",
        compute="_compute_price_unit",
        store=True,
    )
    remaining_qty = fields.Float(
        "Remaing quantity",
        compute="_compute_remaining_qty",
        store=True,
    )
    in_move_line_id = fields.Many2one(
        "res.currency.move.line",
        string="Incoming move line",
        readonly=True,
    )
    out_line_ids = fields.One2many(
        "res.currency.move.line",
        "in_move_line_id",
        "Outgoing Move Lines",
        readonly=True,
    )
    account_move_ids = fields.One2many(
        "account.move",
        "res_currency_move_line_id",
        string="Journal Entries",
        readonly=True,
    )

    @api.depends("amount", "quantity")
    def _compute_price_unit(self):
        for rec in self:
            if rec.quantity:
                rec.price_unit = rec.amount / rec.quantity

    @api.model
    def _get_in_base_domain(self, company_id=False):
        return [("company_id", "=", company_id), ("direction", "=", "inbound")]

    @api.depends("out_line_ids")
    def _compute_remaining_qty(self):
        for rec in self:
            out_qty = sum(rec.mapped("out_line_ids").mapped("quantity"))
            rec.remaining_qty = rec.quantity - out_qty

    @api.model
    def _prepare_credit_aml(self):
        return {
            "name": "",
            "account_id": self.move_id.credit_account_id.id,
            "debit": 0.0,
            "credit": self.amount,
            "currency_id": self.currency_id.id,
            "amount_currency": -1 * self.quantity,
        }

    def _prepare_debit_aml(self):
        return {
            "name": "",
            "account_id": self.move_id.debit_account_id.id,
            "debit": self.amount,
            "credit": 0.0,
            "currency_id": self.currency_id.id,
            "amount_currency": self.quantity,
        }

    @api.model
    def _prepare_account_move(self):
        data = {
            "journal_id": self.move_id.journal_id.id,
            "date": self.date,
            "ref": self.move_id.name,
            "company_id": self.company_id.id,
            "res_currency_move_line_id": self.id,
        }
        aml_credit_data = self._prepare_credit_aml()
        aml_debit_data = self._prepare_debit_aml()
        data["line_ids"] = [(0, 0, aml_debit_data), (0, 0, aml_credit_data)]
        return data

    @api.model
    def create(self, vals):
        move_line = super().create(vals)
        am_data = move_line._prepare_account_move()
        account_move = self.env["account.move"].create(am_data)
        account_move.action_post()
        return move_line

    def unlink(self):
        if self.mapped("account_move_ids"):
            raise UserError(
                _("You can not delete a currency move line" "that is already posted")
            )
        return super().unlink()
