import logging
from unittest.mock import Mock, patch

from odoo.tests.common import TransactionCase, tagged

_logger = logging.getLogger(__name__)

PATCH_PATH = "requests.post"


@tagged("post_install", "-at_install")
class TestBinanceP2PProvider(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.usd = self.env.ref("base.USD")
        self.company.write({"currency_id": self.usd.id})
        self.provider = self.env["res.currency.rate.provider"].create(
            {
                "name": "Binance P2P",
                "service": "bnb_p2p",
                "p2p_transaction_type": "BUY",
            }
        )

    def test_get_supported_currencies_bnb_p2p(self):
        supported = self.provider._get_supported_currencies()
        self.assertEqual(set(supported), {"USDT", "USDC"})

    @patch(PATCH_PATH)
    def test_get_offers_p2p_avg_ok(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "000000",
            "data": [
                {"adv": {"price": "40.00"}},
                {"adv": {"price": "42.00"}},
                {"adv": {"price": "41.00"}},
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = self.provider.get_offers_p2p_avg("USDT", "BUY", limit=3)
        self.assertTrue(res)
        rate = res
        self.assertAlmostEqual(rate, 1 / 41.0, places=6)

        mock_post.assert_called_once()
        called_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(called_payload["fiat"], "USD")
        self.assertEqual(called_payload["asset"], "USDT")
        self.assertEqual(called_payload["tradeType"], "BUY")

    @patch(PATCH_PATH)
    def test_get_offers_p2p_avg_empty_data(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "000000",
            "data": [],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = self.provider.get_offers_p2p_avg("USDT", "BUY")
        self.assertFalse(res)

    @patch(PATCH_PATH)
    def test_get_offers_p2p_avg_error_code(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "000001",
            "data": [],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        res = self.provider.get_offers_p2p_avg("USDT", "BUY")
        self.assertFalse(res)

    @patch(PATCH_PATH)
    def test_obtain_rates_bnb_p2p(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": "000000",
            "data": [
                {"adv": {"price": "40.00"}},
                {"adv": {"price": "40.50"}},
            ],
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        content = self.provider._obtain_rates(
            base_currency=self.usd,
            currencies=["USDT", "USDC"],
            date_from=False,
            date_to=False,
        )

        self.assertEqual(len(content), 1)
        dt_key = list(content.keys())[0]
        self.assertIn("USDT", content[dt_key])
        self.assertIn("USDC", content[dt_key])
        self.assertAlmostEqual(content[dt_key]["USDT"], 1 / 40.25, places=6)
        self.assertAlmostEqual(content[dt_key]["USDC"], 1 / 40.25, places=6)
