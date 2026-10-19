# Copyright 2023 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import requests
from freezegun import freeze_time

from odoo import fields
from odoo.fields import Command
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

    @freeze_time("2026-10-16")
    def test_cron(self):
        self.xe_provider._scheduled_update()
        rates = self.CurrencyRate.search([])
        self.assertEqual(len(rates), 1)
        self.assertEqual(rates.currency_id, self.usd_currency)

    @freeze_time("2026-10-19")
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

    @freeze_time("2026-10-19")
    def test_wizard_jod(self):
        jod_currency = self.env.ref("base.JOD")
        jod_currency.active = True
        self.xe_provider.write(
            {
                "currency_ids": [Command.set([jod_currency.id])],
            }
        )
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, self.xe_provider.ids)])
            .create(
                {
                    "date_from": "2026-10-15",
                    "date_to": "2026-10-16",
                }
            )
        )
        wizard.action_update()
        self.assertEqual(len(jod_currency.rate_ids), 2)
        self.assertIn(
            fields.Date.from_string("2026-10-15"), jod_currency.rate_ids.mapped("name")
        )
        self.assertIn(
            fields.Date.from_string("2026-10-16"), jod_currency.rate_ids.mapped("name")
        )
