# Copyright 2021 ForgeFlow S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_STATES = [
    ("draft", "Draft"),
    ("posted", "Posted"),
    ("cancel", "Cancelled"),
]

_DIRECTIONS = [
    ("inbound", "Receive"),
    ("outbound", "Send"),
]


class ResCurrencyMove(models.Model):
    _name = "res.currency.move"
    _description = "Currency Move"

    name = fields.Char(
        index=True,
        required=True,
        copy=False,
        default=lambda self: _("New"),
        readonly=True,
    )
    payment_id = fields.Many2one(
        "account.payment",
        string="Payment",
        readonly=True,
        copy=False,
        ondelete="cascade",
    )
    amount = fields.Float(
        "Amount",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
        ondelete="restrict",
        required=True,
        states={"draft": [("readonly", False)]},
        domain="[('inventoried', '=', True)]",
    )
    date = fields.Date(
        string="Move Date",
        readonly=True,
        default=fields.Date.context_today,
        required=True,
        copy=False,
        states={"draft": [("readonly", False)]},
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Account Journal",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )
    debit_account_id = fields.Many2one("account.account", compute="_compute_accounts")
    credit_account_id = fields.Many2one("account.account", compute="_compute_accounts")
    state = fields.Selection(
        selection=_STATES,
        required=True,
        readonly=True,
        default="draft",
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        change_default=True,
        default=lambda self: self.env["res.company"]._company_default_get(
            "res.currency.move"
        ),
    )
    direction = fields.Selection(
        selection=_DIRECTIONS,
        string="Direction",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    line_ids = fields.One2many(
        "res.currency.move.line",
        "move_id",
        string="Currency move lines",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.depends("currency_id", "journal_id", "direction")
    def _compute_accounts(self):
        for rec in self:
            inventory_account = self.currency_id.with_company(
                self.company_id
            ).inventory_account_id

            if self.direction == "inbound":
                rec.debit_account_id = inventory_account
                rec.credit_account_id = self.journal_id.default_account_id
            else:
                rec.debit_account_id = self.journal_id.default_account_id
                rec.credit_account_id = inventory_account

    def _get_sequence(self):
        return "res.currency.move"

    @api.model
    def create(self, vals):
        if not vals.get("name"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                self._get_sequence()
            ) or _("New")
        return super().create(vals)

    def _prepare_incoming_move_line(self):
        self.ensure_one()
        amount = self.currency_id._convert(
            self.amount,
            self.company_id.currency_id,
            self.company_id,
            self.date,
        )
        return {
            "move_id": self.id,
            "quantity": self.amount,
            "date": self.date,
            "amount": amount,
        }

    def _prepare_outgoing_move_line(self, candidate, qty):
        self.ensure_one()
        return {
            "move_id": self.id,
            "quantity": qty,
            "date": self.date,
            "in_move_line_id": candidate.id,
            "amount": candidate.price_unit * qty,
        }

    def _get_fifo_candidates_in_move_line(self):
        """Find IN moves that can be used to value OUT moves."""
        self.ensure_one()
        domain = [
            ("currency_id", "=", self.currency_id.id),
            ("remaining_qty", ">", 0.0),
        ] + self.env["res.currency.move.line"]._get_in_base_domain(
            company_id=self.company_id.id
        )
        candidates = self.env["res.currency.move.line"].search(domain, order="date, id")
        return candidates

    def _run_fifo(self):
        self.ensure_one()
        qty_to_take_on_candidates = self.amount
        candidates = self._get_fifo_candidates_in_move_line()
        for candidate in candidates.filtered("remaining_qty"):
            if candidate.remaining_qty <= qty_to_take_on_candidates:
                qty_taken_on_candidate = candidate.remaining_qty
            else:
                qty_taken_on_candidate = qty_to_take_on_candidates
            move_line_data = self._prepare_outgoing_move_line(
                candidate, qty_taken_on_candidate
            )
            self.env["res.currency.move.line"].create(move_line_data)
            qty_to_take_on_candidates -= qty_taken_on_candidate
        if not self.currency_id.is_zero(qty_to_take_on_candidates):
            raise ValidationError(
                _(
                    "It was not possible to find enough "
                    "currency units from incoming moves"
                )
            )
        return True

    def _post(self):
        for rec in self:
            if rec.direction == "inbound":
                move_line_data = rec._prepare_incoming_move_line()
                self.env["res.currency.move.line"].create(move_line_data)
            elif rec.direction == "outbound":
                # Currency we only support fifo valuation method.
                self._run_fifo()
            rec.state = "posted"

    def action_post(self):
        self._post()
        return False

    def action_draft(self):
        return self.write({"state": "draft"})

    def action_cancel(self):
        force_delete = self.env.context.get("force_delete", False)
        for rec in self:
            if rec.payment_id and not force_delete:
                raise UserError(
                    _(
                        "You can not cancel a currency move "
                        "that is linked to a payment. "
                        "Please cancel the payment first."
                    )
                )
            for move in rec.line_ids.mapped("account_move_ids"):
                move.button_cancel()
            rec.write({"state": "cancel"})

    def unlink(self):
        if self.mapped("line_ids"):
            raise UserError(
                _("You can not delete a currency move " "that is already posted")
            )
        return super().unlink()

    @api.constrains("amount")
    def _constrain_amount(self):
        for rec in self:
            if rec.amount <= 0.0:
                raise ValidationError(_("The amount must always be positive."))
