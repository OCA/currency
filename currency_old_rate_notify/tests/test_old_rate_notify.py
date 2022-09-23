# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestCurrencyOldRateNotify(TransactionCase):
    def test_cron_method(self):
        self.env.ref("base.BOB").write({"active": True})
        self.env["res.currency.rate"].notify_rates_too_old()
