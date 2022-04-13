# © 2022 sewisoft
# © 2017 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestCurrencyRateUpdateDb(common.SavepointCase):
    at_install = False
    post_install = True

    def setUp(self):
        super(TestCurrencyRateUpdateDb, self).setUp()
        self.company = self.env['res.company'].create({
            'name': 'Test company',
            'currency_id': self.env.ref('base.EUR').id,
        })
        self.env.user.company_ids += self.company
        self.env.user.company_id = self.company
        self.currency = self.env.ref('base.USD')
        self.update_service = self.env['currency.rate.update.service'].create({
            'service': 'DBM1ASK',
            'currency_to_update':
                [(4, self.currency.id),
                 (4, self.env.user.company_id.currency_id.id)]
        })
        currency_rates = self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        currency_rates.unlink()

    def test_currency_rate_update_dbm1ask(self):
        self.assertFalse(self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        )
        self.update_service.service = 'DBM1ASK'
        self.update_service.refresh_currency()
        currency_rates = self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        self.assertTrue(currency_rates)

    def test_currency_rate_update_dbm1bid(self):
        self.assertFalse(self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        )
        self.update_service.service = 'DBM1BID'
        self.update_service.refresh_currency()
        currency_rates = self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        self.assertTrue(currency_rates)

    def test_currency_rate_update_dbm6ask(self):
        self.assertFalse(self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        )
        self.update_service.service = 'DBM6ASK'
        self.update_service.refresh_currency()
        currency_rates = self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        self.assertTrue(currency_rates)

    def test_currency_rate_update_dbm6bid(self):
        self.assertFalse(self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        )
        self.update_service.service = 'DBM6BID'
        self.update_service.refresh_currency()
        currency_rates = self.env['res.currency.rate'].search(
            [('currency_id', '=', self.currency.id)])
        self.assertTrue(currency_rates)
