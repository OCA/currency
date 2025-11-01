from odoo.tests.common import TransactionCase, tagged
from unittest.mock import patch, Mock

BCV_HTML = """
<html>
  <body>
    <div id="dolar">
      <div>
        <div>
          <div></div>
          <div><strong>223,96220000</strong></div>
        </div>
      </div>
    </div>
    <div id="euro">
      <div>
        <div>
          <div></div>
          <div><strong>258,14779020</strong></div>
        </div>
      </div>
    </div>
    <div id="yuan">
      <div>
        <div>
          <div></div>
          <div><strong>31,47127761</strong></div>
        </div>
      </div>
    </div>
    <div id="lira">
      <div>
        <div>
          <div></div>
          <div><strong>5,32663744</strong></div>
        </div>
      </div>
    </div>
    <div id="rublo">
      <div>
        <div>
          <div></div>
          <div><strong>2,77232407</strong></div>
        </div>
      </div>
    </div>
  </body>
</html>
"""


@tagged("post_install", "-at_install")
class TestBCVRateProvider(TransactionCase):
    def setUp(self):
        super().setUp()
        self.provider = self.env["res.currency.rate.provider"].create(
            {
                "name": "BCV",
                "service": "bcv",
            }
        )

    def test_get_supported_currencies_bcv(self):
        supported = self.provider._get_supported_currencies()
        self.assertIn("USD", supported)
        self.assertIn("EUR", supported)
        self.assertIn("CNY", supported)
        self.assertIn("TRY", supported)
        self.assertIn("RUB", supported)

    @patch("requests.get")
    def test_obtain_rates_bcv(self, mock_get):
        response = Mock()
        response.content = BCV_HTML.encode()
        mock_get.return_value = response

        usd = self.env.ref("base.USD")
        eur = self.env.ref("base.EUR")
        ves = self.env.ref("base.VES", raise_if_not_found=False) or self.env.ref("base.VEF", raise_if_not_found=False)

        base_currency = ves or usd
        currencies = [usd.name, eur.name]

        content = self.provider._obtain_rates(
            base_currency=base_currency,
            currencies=currencies,
            date_from=False,
            date_to=False,
        )

        self.assertEqual(len(content), 1)
        dt_key = list(content.keys())[0]
        self.assertIn("USD", content[dt_key])
        self.assertIn("EUR", content[dt_key])
        self.assertAlmostEqual(content[dt_key]["USD"], 0.004465039189648968, places=6)
        self.assertAlmostEqual(content[dt_key]["EUR"], 0.003873749991139766, places=6)
