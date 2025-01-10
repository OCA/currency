# Copyright 2025 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

import requests_mock

from odoo import fields
from odoo.tests import common


class TestResCurrencyRateProviderBanxico(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.yesterday = cls.today - timedelta(days=1)
        cls.currency_rate = cls.env["res.currency.rate"]
        cls.usd_currency = cls.env.ref("base.USD")
        cls.company = cls.env["res.company"].create(
            {"name": "Test company", "currency_id": cls.env.ref("base.MXN").id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company
        cls.banxico_provider = cls.env["res.currency.rate.provider"].create(
            {
                "service": "banxico",
                "banxico_token": "test_token",
                "company_id": cls.company.id,
                "last_successful_run": cls.yesterday,
                "currency_ids": [
                    (4, cls.usd_currency.id),
                ],
            }
        )
        cls.currency_rate.search([]).unlink()

    def mock_response(self, mocker):
        """Helper function to mock the API response."""
        url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF60653/datos/oportuno"
        mocker.get(
            url,
            json={
                "bmx": {
                    "series": [
                        {
                            "idSerie": "SF60653",
                            "titulo": "Test Title",
                            "datos": [
                                {
                                    "fecha": self.today.strftime("%d/%m/%Y"),
                                    "dato": "20.4742",
                                }
                            ],
                        }
                    ]
                }
            },
        )
        url = (
            "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF60653/datos/"
            "{self.yesterday.strftime('%d/%m/%Y')}/{self.today.strftime('%d/%m/%Y')}"
        )
        mocker.get(
            url,
            json={
                "bmx": {
                    "series": [
                        {
                            "idSerie": "SF60653",
                            "titulo": "Test Title",
                            "datos": [
                                {
                                    "fecha": self.yesterday.strftime("%d/%m/%Y"),
                                    "dato": "20.3440",
                                },
                                {
                                    "fecha": self.today.strftime("%d/%m/%Y"),
                                    "dato": "20.3823",
                                },
                            ],
                        }
                    ]
                }
            },
        )

    def test_cron(self):
        with requests_mock.Mocker() as mocker:
            self.mock_response(mocker)
            self.banxico_provider._scheduled_update()
            rates = self.currency_rate.search([("company_id", "=", self.company.id)])

            self.assertEqual(len(rates), 1)
            self.assertEqual(rates.currency_id, self.usd_currency)
            self.assertAlmostEqual(rates.rate, 1 / 20.4742, places=4)

    def test_wizard(self):
        with requests_mock.Mocker() as mocker:
            self.mock_response(mocker)

            wizard = (
                self.env["res.currency.rate.update.wizard"]
                .with_context(
                    default_provider_ids=[(6, False, self.banxico_provider.ids)]
                )
                .create(
                    {
                        "date_from": self.yesterday,
                        "date_to": self.today,
                    }
                )
            )
            wizard.action_update()

            rates = self.currency_rate.search([("company_id", "=", self.company.id)])
            self.assertEqual(len(rates), 2)

            yesterday_rate = rates.filtered(lambda r: r.name == self.yesterday)
            self.assertEqual(len(yesterday_rate), 1)
            self.assertEqual(yesterday_rate.currency_id, self.usd_currency)
            self.assertAlmostEqual(yesterday_rate.rate, 1 / 20.3440, places=4)

            today_rate = rates.filtered(lambda r: r.name == self.today)
            self.assertEqual(len(today_rate), 1)
            self.assertEqual(today_rate.currency_id, self.usd_currency)
            self.assertAlmostEqual(today_rate.rate, 1 / 20.3823, places=4)
