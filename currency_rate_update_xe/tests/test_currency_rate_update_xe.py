# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import fields
from odoo.tests import common


class TestResCurrencyRateProviderXE(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Company = cls.env["res.company"]
        cls.CurrencyRate = cls.env["res.currency.rate"]
        cls.CurrencyRateProvider = cls.env["res.currency.rate.provider"]

        cls.today = fields.Date.today()
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.company = cls.Company.create(
            {"name": "Test company", "currency_id": cls.eur_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.xe_provider = cls.CurrencyRateProvider.create(
            {
                "service": "XE",
                "currency_ids": [
                    (4, cls.usd_currency.id),
                    (4, cls.eur_currency.id),
                ],
            }
        )
        cls.CurrencyRate.search([]).unlink()

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
