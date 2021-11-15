# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.addons.account.tests import account_test_no_chart
from odoo.exceptions import MissingError


class TestCurrencyRateUpdate(account_test_no_chart.TestAccountNoChartCommon):
    def setUp(self):
        super().setUp()
        self.company_obj = self.env['res.company']
        self.today = fields.Date.today()
        self.eur_currency = self.env.ref('base.EUR')
        self.jpy_currency = self.env.ref('base.JPY')
        if self.env.user.company_id.currency_id == self.jpy_currency:
            self.currency = self.eur_currency
        else:
            self.currency = self.jpy_currency
        self.env['account.move.line'].with_context(
            check_move_validity=False)
        self.move = self.env['account.move'].create({
            'name': 'move name',
            'journal_id': self.sale_journal0.id,
            'date': self.today,
            'line_ids': [
                (0, 0, {
                    'name': 'debit',
                    'account_id': self.account_receivable.id,
                    'amount_currency': 1100,
                    'currency_id': self.currency.id,
                }),
                (0, 0, {
                    'name': 'credit',
                    'account_id': self.account_payable.id,
                    'amount_currency': -1100,
                    'currency_id': self.currency.id,
                }),
            ],
        })
        self.rates = self.env['res.currency.rate'].create([
            {
                'currency_id': self.eur_currency.id,
                'rate': 0.87
            },
            {
                'currency_id': self.jpy_currency.id,
                'rate': 111.73
            },
        ])
        self.currency_check_obj = self.env['account.move.line.currency.check']
        values = []
        for line in self.move.line_ids:
            values.append({
                'line_id': line.id,
                'rate_partner': self.rates[0].id,
                'rate_company': self.rates[1].id,
            })
        self.currency_check_obj.create(values)
        self.currency_checks = self.currency_check_obj.search([])
        self.move.line_ids._onchange_amount_currency()

    def test_update_rate_aml(self):
        """Check that the amounts get updated when calling
        action_rebase_currency_partner and action_rebase_currency_company after
        intentionally mismatching (credit or debit) and amount_currency."""
        date_from = date_to = self.today
        line_limit = 2
        ref = False
        self.assertEqual(len(self.currency_checks), 2)
        for line in self.move.line_ids:
            if line.debit > 0:
                line.debit += 50.0
            elif line.credit > 0:
                line.credit += 50.0
        self.assertNotEqual(
            self.move.line_ids[0].debit or self.move.line_ids[0].credit,
            abs(self.move.line_ids[0].amount_currency)
        )
        self.assertNotEqual(
            self.move.line_ids[1].debit or self.move.line_ids[1].credit,
            abs(self.move.line_ids[1].amount_currency)
        )
        self.currency_checks.action_rebase_currency_partner()
        # Check that the check lines are deleted after being rebased
        with self.assertRaises(MissingError):
            self.currency_checks.mapped('move_id')
        self.assertEqual(
            self.move.line_ids[0].debit or self.move.line_ids[0].credit,
            abs(self.move.line_ids[0].currency_id._convert(
                self.move.line_ids[0].amount_currency,
                self.move.line_ids[0].company_currency_id,
                self.move.line_ids[0].company_id, self.today
            ))
        )
        self.assertEqual(
            self.move.line_ids[1].debit or self.move.line_ids[1].credit,
            abs(self.move.line_ids[1].currency_id._convert(
                self.move.line_ids[1].amount_currency,
                self.move.line_ids[1].company_currency_id,
                self.move.line_ids[1].company_id, self.today
            ))
        )

        # Do the same thing but for action_rebase_currency_company
        for line in self.move.line_ids:
            if line.debit > 0:
                line.debit += 50.0
            elif line.credit > 0:
                line.credit += 50.0
        self.assertNotEqual(
            self.move.line_ids[0].debit or self.move.line_ids[0].credit,
            abs(self.move.line_ids[0].amount_currency)
        )
        self.assertNotEqual(
            self.move.line_ids[1].debit or self.move.line_ids[1].credit,
            abs(self.move.line_ids[1].amount_currency)
        )
        self.currency_check_obj.action_update_check_lines(
            date_from, date_to, line_limit, ref
        )
        self.currency_checks = self.currency_check_obj.search([])
        self.currency_checks.action_rebase_currency_company()
        self.assertEqual(
            self.move.line_ids[0].debit or self.move.line_ids[0].credit,
            abs(self.move.line_ids[0].currency_id._convert(
                self.move.line_ids[0].amount_currency,
                self.move.line_ids[0].company_currency_id,
                self.move.line_ids[0].company_id, self.today
            ))
        )
        self.assertEqual(
            self.move.line_ids[1].debit or self.move.line_ids[1].credit,
            abs(self.move.line_ids[1].currency_id._convert(
                self.move.line_ids[1].amount_currency,
                self.move.line_ids[1].company_currency_id,
                self.move.line_ids[1].company_id, self.today
            ))
        )
