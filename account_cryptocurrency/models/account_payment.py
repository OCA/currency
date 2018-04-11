# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    res_currency_move_ids = fields.One2many(
        'res.currency.move', 'payment_id', readonly=True, copy=False,
        ondelete='cascade')

    has_currency_move_ids = fields.Boolean(
        compute="_compute_has_currency_move_ids",
        help="Technical field used for usability purposes")

    @api.depends('invoice_ids')
    def _compute_has_currency_move_ids(self):
        self.has_currency_move_ids = bool(self.res_currency_move_ids)

    def _prepare_currency_inventory_move(self, amount):
        return {
            'payment_id': self.id,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id,
            'date': self.payment_date,
            'direction': self.payment_type,
            'journal_id': self.journal_id.id,
        }

    def _create_payment_entry(self, amount):
        res = super()._create_payment_entry(amount)
        if self.currency_id.inventoried:
            curr_inv_move_data = self._prepare_currency_inventory_move(amount)
            curr_inv_move = self.env['res.currency.move'].create(
                curr_inv_move_data)
            curr_inv_move.post()
        return res

    def cancel(self):
        self.res_currency_move_ids.with_context(force_cancel=True).cancel()
        self.res_currency_move_ids.unlink()
        return super().cancel()

    def button_currency_moves(self):
        return {
            'name': _('Currency moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.currency.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [
                x.id for x in self.res_currency_move_ids])],
        }

    @api.onchange('currency_id')
    def _onchange_currency(self):
        if self.currency_id and self.currency_id.inventoried:
                return {'domain': {'journal_id': [('currency_id', '=',
                                                   self.currency_id.id)]}}
        return {}

    @api.constrains('payment_type')
    def _check_payment_type_crypto(self):
        for rec in self:
            if rec.currency_id.inventoried and rec.payment_type == 'transfer':
                raise exceptions.Warning(
                    _('You cannot make internal transfers using crypto '
                      'currencies.'))
