# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import requests
from freezegun import freeze_time

from odoo import fields
from odoo.fields import Command
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestResCurrencyRateProviderFrankfurter(BaseCommon):
    @classmethod
    def setUpClass(cls):
        cls._super_send = requests.Session.send
        super().setUpClass()
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.company = cls.env["res.company"].create(
            {"name": "Test company", "currency_id": cls.eur_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.provider = cls.env["res.currency.rate.provider"].create(
            {
                "service": "frankfurter",
                "currency_ids": [Command.set([cls.usd_currency.id])],
            }
        )

    @classmethod
    def _request_handler(cls, s, r, /, **kw):
        """Don't block external requests."""
        return cls._super_send(s, r, **kw)

    def test_supported_currencies(self):
        currencies = self.provider._get_supported_currencies()
        self.assertIn("JOD", currencies)

    @freeze_time("2026-10-19")
    @mute_logger("odoo.models.unlink")
    def test_wizard(self):
        self.usd_currency.rate_ids.unlink()
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[Command.set([self.provider.id])])
            .create({})
        )
        wizard.action_update()
        self.assertEqual(len(self.usd_currency.rate_ids), 1)
        self.assertEqual(
            self.usd_currency.rate_ids.name, fields.Date.from_string("2026-10-19")
        )

    @freeze_time("2026-10-19")
    @mute_logger("odoo.models.unlink")
    def test_wizard_jod(self):
        jod_currency = self.env.ref("base.JOD")
        jod_currency.active = True
        jod_currency.rate_ids.unlink()
        self.provider.write({"currency_ids": [Command.set([jod_currency.id])]})
        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[Command.set([self.provider.id])])
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
