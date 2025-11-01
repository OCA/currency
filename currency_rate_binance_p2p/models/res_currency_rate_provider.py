import logging
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

TIMEOUT = 5000
CURRENCIES = ("USDT", "USDC")
URL_BINANCE_P2P = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"


class ResCurrencyRateProvider(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("bnb_p2p", "Binance P2P API")],
        ondelete={"bnb_p2p": "set default"},
    )

    p2p_transaction_type = fields.Selection(
        selection=[("BUY", "Buy"), ("SELL", "Sell")],
        default="BUY",
        string="P2P Transaction Type",
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "bnb_p2p":
            return super()._get_supported_currencies()
        return CURRENCIES

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        dt = datetime.now().isoformat()
        if self.service != "bnb_p2p":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)

        content = defaultdict(dict)

        bnb_data = {}
        for currency in currencies:
            value = self.get_offers_p2p_avg(currency, self.p2p_transaction_type)
            if value:
                bnb_data[currency] = value

        for k, v in bnb_data.items():
            content[dt][k] = v
        return content

    def get_offers_p2p_avg(self, to_currency=False, transaction_type="BUY", limit=5):
        if not to_currency:
            return False
        try:
            fiat_currency = self.env.company.currency_id.name

            payload = {
                "fiat": fiat_currency,
                "asset": to_currency,
                "page": 1,
                "rows": limit,
                "payTypes": [],
                "tradeType": transaction_type,
                "publisherType": None,
                "countries": [],
                "proMerchantAds": False,
            }

            response = requests.post(URL_BINANCE_P2P, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data and data.get("code") == "000000" and data.get("data"):
                prices = []
                for offer in data["data"]:
                    price_str = offer["adv"]["price"]
                    prices.append(Decimal(price_str))

                if prices:
                    avg_price = sum(prices) / len(prices)

                    return 1.0 / float(avg_price)
                else:
                    return False
            else:
                return False
        except Exception:
            return False
