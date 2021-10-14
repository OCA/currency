# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.tools import float_compare, formatLang
from .account_move import bypass_update_checks


class AccountMoveLineCurrencyCheck(models.Model):
    _name = 'account.move.line.currency.check'
    _inherits = {'account.move.line': 'line_id'}
    _description = 'Journal Item Currency Check Wizard'
    _rec_name = 'line_id'

    line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Journal Item',
        required=True,
        ondelete='CASCADE',
        index=True,
    )
    amount = fields.Monetary(
        string='Amount Company Currency',
        help='Amount Currency converted to company currency '
             '(this will replace Debit or Credit with the '
             '"Copy Amount Company Currency to debit/credit" button)',
        currency_field='company_currency_id',
        compute='_compute_amount', store=False,
    )
    alt_amount_currency = fields.Monetary(
        string='Amount Partner Currency',
        help='Debit or credit converted to partner currency '
             '(this will replace Amount Currency with the '
             '"Copy Amount Partner Currency to Amount Currency" button)',
        currency_field='currency_id',
        compute='_compute_alt_amount_currency', store=False,
    )
    rate_partner = fields.Many2one('res.currency.rate')
    rate_company = fields.Many2one('res.currency.rate')

    _sql_constraints = [
        ('line_id_uniq', 'UNIQUE(line_id)',
         _('The reference to journal items must be unique.')),
    ]

    @api.one
    def _compute_amount(self):
        company_currency_id = self.account_id.company_id.currency_id
        self.amount = self.currency_id._convert(
            from_amount=self.amount_currency,
            to_currency=company_currency_id,
            company=self.company_id,
            date=self.date
        )

    @api.one
    def _compute_alt_amount_currency(self):
        sign = (1, -1)[self.amount_currency < 0]
        if self.debit:
            from_amount = self.debit * sign
        elif self.credit:
            from_amount = self.credit * sign
        else:
            from_amount = 0
        self.alt_amount_currency = self.company_currency_id._convert(
            from_amount=from_amount,
            to_currency=self.currency_id,
            company=self.company_id,
            date=self.date
        )

    @api.model_cr
    def action_update_check_lines(self, date_from, date_to, line_limit, ref):
        """Upsert journal items into account.move.line.currency.check if they have
        amounts that do not match up according to the parameters received from the
        wizard and the exchange rates in Odoo."""
        precision = self.env['decimal.precision'].precision_get('Account')
        domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('company_id', '=', self.env.user.company_id.id),
        ]
        if ref:
            domain.extend([
                ('ref', 'ilike', ref)
            ])
        moves = self.env['account.move'].search(domain)
        moves = moves.filtered(lambda move: len(move.line_ids) <= line_limit)
        lines = moves.mapped('line_ids')
        create_values = []
        write_values = []
        for line in lines:
            # Even if we already have the line in the table, recompute the amounts
            # and perform an upsert if they don't match.
            company_currency_id = line.account_id.company_id.currency_id
            if (
                line.currency_id
                and company_currency_id
                and line.currency_id != company_currency_id
                and line.date
            ):
                # Note: _convert will take the most recent (older) date if one for the
                # given date does not exist. To rephrase: a rate that is newer than the
                # requested date will not be used.
                amount = line.currency_id._convert(
                    from_amount=line.amount_currency,
                    to_currency=company_currency_id,
                    company=line.company_id,
                    date=line.date
                )
                # Check lines if the converted amount_currency does not match up with
                # debit or credit
                if (
                    amount > 0 and float_compare(
                        line.debit, abs(amount), precision_digits=precision)
                ) or (
                    amount < 0 and float_compare(
                        line.credit, abs(amount), precision_digits=precision
                    )
                ):
                    domain = [
                        ('name', '=', line.date),
                        ('company_id', '=', self.env.user.company_id.id),
                    ]
                    rate_partner = self.env['res.currency.rate'].search(
                        domain + [('currency_id', '=', line.currency_id.id)]
                    )
                    rate_company = self.env['res.currency.rate'].search(
                        domain + [('currency_id', '=', line.company_currency_id.id)]
                    )
                    values = {
                        'line_id': line.id,
                        'rate_partner': rate_partner.id,
                        'rate_company': rate_company.id,
                    }
                    check_line = self.search([('line_id', '=', line.id)])
                    if len(check_line) > 0:
                        check_line.write(values)
                        write_values.append(values)
                    else:
                        create_values.append(values)
        if create_values:
            self.create(create_values)
        return write_values + create_values

    @api.model
    def _get_converted_amount(
        self, move, line, from_amount, from_currency, to_currency
    ):
        if len(move.line_ids) > 2:
            raise NotImplementedError(
                _(
                    "Recomputing Entries with more than two Items is not yet "
                    "implemented."
                )
            )
        assert (
            move.line_ids[0].credit == move.line_ids[1].debit
            and move.line_ids[1].credit == move.line_ids[0].debit
        )
        amount = abs(from_currency._convert(
            from_amount=from_amount,
            to_currency=to_currency,
            company=line.company_id,
            date=line.date)
        )
        return amount

    @api.model
    def _message_post(self, env, move, currency_company, amount, old_amount):
        """Post a message with the old and new amount to the invoices related to the
        given move. The symbol is determined based on whether the partner or company
        currency is used (indicated here with the currency_company bool."""
        link_template = '<a href="#" data-oe-model="%s" data-oe-id="%d">%s</a>'
        move.mapped('line_ids').mapped(lambda l: l.invoice_id.message_post(
            body=_(
                "{link} has been recomputed from {old_amount} to "
                "{new_amount} because the exchange rate was "
                "updated."
            ).format(
                link=link_template % (
                    l._name, l.id, l.display_name or _('Unnamed')
                    ),
                old_amount=formatLang(
                    env,
                    value=abs(old_amount),
                    currency_obj=l.currency_id
                    ) if currency_company
                else formatLang(
                    env,
                    value=old_amount,
                    currency_obj=l.company_currency_id
                    ),
                new_amount=formatLang(
                    env,
                    value=abs(amount),
                    currency_obj=l.currency_id
                    ) if currency_company
                else formatLang(
                    env,
                    value=abs(amount),
                    currency_obj=l.company_currency_id
                    )
            )
        ))

    @api.multi
    def action_rebase_currency_partner(self):
        """Recompute debit or credit based on the value of amount_currency."""
        moves = self.mapped('move_id')
        to_unlink = self.browse()
        for move in moves:
            line = move.line_ids[0]
            company_currency_id = line.account_id.company_id.currency_id
            amount = self._get_converted_amount(
                move=move,
                line=line,
                from_amount=line.amount_currency,
                from_currency=line.currency_id,
                to_currency=company_currency_id
            )

            old_amount = move.line_ids[0].credit or move.line_ids[0].debit
            move.with_context(__bypass_update_checks=bypass_update_checks).write({
                'line_ids': [
                    (1, move.line_ids[0].id, {
                        'debit': amount if move.line_ids[0].debit > 0 else 0,
                        'credit': amount if move.line_ids[0].credit > 0 else 0,
                    }),
                    (1, move.line_ids[1].id, {
                        'debit': amount if move.line_ids[1].debit > 0 else 0,
                        'credit': amount if move.line_ids[1].credit > 0 else 0,
                    })
                ],
            })
            to_unlink |= self.search([('line_id', 'in', move.line_ids.ids)])

            self._message_post(self.env, move, False, amount, old_amount)
        to_unlink.unlink()

    @api.multi
    def action_rebase_currency_company(self):
        """Recompute amount_currency based on the value of debit or credit."""
        to_unlink = self.browse()
        moves = self.mapped('move_id')
        for move in moves:
            if move.line_ids[0].debit:
                debit_line = move.line_ids[0]
            else:
                debit_line = move.line_ids[1]
            company_currency_id = debit_line.account_id.company_id.currency_id
            amount = self._get_converted_amount(
                move=move,
                line=debit_line,
                from_amount=debit_line.debit,
                from_currency=company_currency_id,
                to_currency=debit_line.currency_id
            )

            old_amount = move.line_ids[0].amount_currency
            move.with_context(__bypass_update_checks=bypass_update_checks).write({
                'line_ids': [
                    (1, move.line_ids[0].id, {
                        'amount_currency':
                        amount if move.line_ids[0].amount_currency > 0
                        else amount * -1,
                    }),
                    (1, move.line_ids[1].id, {
                        'amount_currency':
                        amount if move.line_ids[1].amount_currency > 0
                        else amount * -1,
                    })
                ],
            })
            to_unlink |= self.search([('line_id', 'in', move.line_ids.ids)])
            self._message_post(self.env, move, True, amount, old_amount)
        to_unlink.unlink()
