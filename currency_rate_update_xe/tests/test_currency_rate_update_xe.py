# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields
from odoo.tests import common


class TestResCurrencyRateProviderXE(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.Company = self.env["res.company"]
        self.CurrencyRate = self.env["res.currency.rate"]
        self.CurrencyRateProvider = self.env["res.currency.rate.provider"]

        self.today = fields.Date.today()
        self.eur_currency = self.env.ref("base.EUR")
        self.usd_currency = self.env.ref("base.USD")
        self.company = self.Company.create(
            {"name": "Test company", "currency_id": self.eur_currency.id}
        )
        self.env.user.company_ids += self.company
        self.env.company = self.company
        self.xe_provider = self.CurrencyRateProvider.create(
            {
                "service": "XE",
                "currency_ids": [
                    (4, self.usd_currency.id),
                    (4, self.eur_currency.id),
                ],
            }
        )
        self.CurrencyRate.search([]).unlink()

    def test_cron(self):
        self.xe_provider._scheduled_update()
        rates = self.CurrencyRate.search([])
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates.currency_id, self.usd_currency)

    def test_wizard(self):
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, self.xe_provider.ids)])
            .create({})
        )
        wizard.action_update()
        rates = self.CurrencyRate.search([])
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates.currency_id, self.usd_currency)
