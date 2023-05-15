# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import SavepointCase


class TestCurrencyMonthlyRate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")

        cls.usd = cls.env.ref("base.USD")
        cls.eur = cls.env.ref("base.EUR")

        # as fields.Date.today() only calls date.today() and then converts it
        # to ORM format string, we don't need it here
        cls.year = str(date.today().year)

        monthly_rate = cls.env["res.currency.rate.monthly"]

        monthly_rates_to_create = [
            {"month": "01", "rate": 1.20},
            {"month": "02", "rate": 1.40},
        ]
        for r in monthly_rates_to_create:
            r.update(
                {
                    "year": cls.year,
                    "currency_id": cls.usd.id,
                    "company_id": cls.company.id,
                }
            )
            existing_rate = monthly_rate.search(
                [
                    ("name", "=", r["year"] + "-" + r["month"] + "-01"),
                    ("currency_id", "=", r["currency_id"]),
                    ("company_id", "=", r["company_id"]),
                ]
            )
            if not existing_rate:
                monthly_rate.create(r)

        cls.jan_2 = "%s-01-02" % cls.year
        cls.jan_12 = "%s-01-12" % cls.year
        cls.jan_31 = "%s-01-31" % cls.year
        cls.feb_2 = "%s-02-02" % cls.year
        cls.feb_12 = "%s-02-12" % cls.year

    def compute_eur_usd(self, amount, date, monthly):
        self.usd.invalidate_cache()
        self.eur.invalidate_cache()
        if monthly:
            return self.eur.with_context(monthly_rate=True)._convert(
                amount, self.usd, self.company, date
            )
        else:
            return self.eur.with_context()._convert(
                amount, self.usd, self.company, date
            )

    def test_monthly_compute(self):

        self.assertEqual(self.compute_eur_usd(10, self.jan_2, True), 12)
        self.assertEqual(self.compute_eur_usd(10, self.jan_12, True), 12)
        self.assertEqual(self.compute_eur_usd(10, self.jan_31, True), 12)
        self.assertEqual(self.compute_eur_usd(10, self.feb_2, True), 14)
        self.assertEqual(self.compute_eur_usd(10, self.feb_12, True), 14)

    def test_standard_compute(self):
        self.assertEqual(self.compute_eur_usd(10, self.jan_2, False), 12.83)
        self.assertEqual(self.compute_eur_usd(10, self.jan_12, False), 12.83)
        self.assertEqual(self.compute_eur_usd(10, self.jan_31, False), 12.83)
        self.assertEqual(self.compute_eur_usd(10, self.feb_2, False), 12.83)
        self.assertEqual(self.compute_eur_usd(10, self.feb_12, False), 12.83)

    def test_monthly_rate(self):
        self.assertEqual(self.usd.with_context(date=self.jan_2).monthly_rate, 1.2)
        self.assertEqual(self.usd.with_context(date=self.feb_2).monthly_rate, 1.2)

    def test_get_conversion_rate(self):
        currency_model = self.env["res.currency"]
        company = self.env.ref("base.main_company")
        eur_usd_jan_2 = currency_model.with_context(
            date=self.jan_2
        )._get_conversion_rate(
            self.eur,
            self.usd,
            company,
            self.jan_2,
        )
        self.assertEqual(round(eur_usd_jan_2, 2), 1.28)

        monthly_eur_usd_jan_2 = currency_model.with_context(
            date=self.jan_2, monthly_rate=True
        )._get_conversion_rate(
            self.eur,
            self.usd,
            company,
            self.jan_2,
        )
        self.assertEqual(monthly_eur_usd_jan_2, 1.2)
