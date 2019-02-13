# Copyright 2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.tests import common


class TestCurrencyRateInverted(common.SavepointCase):

    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.Currency = self.env['res.currency']
        self.SudoCurrency = self.Currency.sudo()
        self.eur = self.SudoCurrency.search([('name', '=', 'EUR')], limit=1)
        self.usd = self.SudoCurrency.search([('name', '=', 'USD')], limit=1)
        self.gbp = self.SudoCurrency.search(
            [('name', '=', 'GBP'), ('active', '=', False)],
            limit=1
        )
        self.gbp.active = True

    def test_1(self):
        self.eur.write({
            'rate_ids': [
                (0, False, {
                    'name': self.today + timedelta(days=10),
                }),
            ],
        })
        self.usd.write({
            'rate_ids': [
                (0, False, {
                    'name': self.today + timedelta(days=10),
                    'rate': 0.8,
                }),
            ],
        })
        self.gbp.write({
            'rate_ids': [
                (0, False, {
                    'name': self.today + timedelta(days=10),
                    'rate': 1.1,
                }),
            ],
        })

        self.usd.rate_inverted = True
        self.assertAlmostEqual(
            self.eur.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            1.25,
            2
        )
        self.assertAlmostEqual(
            self.usd.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.eur),
            0.8,
            2
        )

        self.gbp.rate_inverted = True
        self.assertAlmostEqual(
            self.gbp.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            1.38,
            2
        )
        self.gbp.rate_inverted = False
        self.assertAlmostEqual(
            self.gbp.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            1.14,
            2
        )

        self.usd.rate_inverted = False
        self.assertAlmostEqual(
            self.eur.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            0.8,
            2
        )
        self.assertAlmostEqual(
            self.usd.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.eur),
            1.25,
            2
        )

        self.gbp.rate_inverted = True
        self.assertAlmostEqual(
            self.gbp.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            0.88,
            2
        )
        self.gbp.rate_inverted = False
        self.assertAlmostEqual(
            self.gbp.with_context({
                'date': self.today + timedelta(days=10),
            }).compute(1.0, self.usd),
            0.73,
            2
        )
