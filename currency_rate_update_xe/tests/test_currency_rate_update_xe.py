# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import requests
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestResCurrencyRateProviderXE(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
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

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_cron(self):
        # Pretend the provider already ran yesterday so _scheduled_update only
        # fetches today's rate (via the "latest" endpoint). Without this, a
        # fresh provider's next_run defaults to today and _scheduled_update
        # computes date_from = today - 1 day, producing one rate per day in
        # the range — which is correct behaviour but makes this assertion
        # depend on whether XE returns a rate for the past-day URL.
        self.xe_provider.last_successful_run = self.today - relativedelta(days=1)
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
