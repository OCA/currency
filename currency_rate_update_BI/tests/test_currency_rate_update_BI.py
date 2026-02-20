# Copyright 2026 PT Solusi Aglis Indonesia (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO
from unittest.mock import patch

from odoo import fields
from odoo.tests import common

# Real XML response format from Bank Indonesia wsKursBI getSubKursLokal3
# Confirmed from live BI webservice (diffgram format, ADO.NET DataSet)
SAMPLE_BI_XML_USD = b"""<?xml version="1.0" encoding="utf-8"?>
<DataSet xmlns="http://tempuri.org/">
  <xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
    <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
      <xs:complexType>
        <xs:choice minOccurs="0" maxOccurs="unbounded">
          <xs:element name="Table">
            <xs:complexType>
              <xs:sequence>
                <xs:element name="id_subkurslokal" type="xs:int" minOccurs="0" />
                <xs:element name="lnk_subkurslokal" type="xs:int" minOccurs="0" />
                <xs:element name="nil_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="beli_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="jual_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="tgl_subkurslokal" type="xs:dateTime" minOccurs="0" />
                <xs:element name="mts_subkurslokal" type="xs:string" minOccurs="0" />
              </xs:sequence>
            </xs:complexType>
          </xs:element>
        </xs:choice>
      </xs:complexType>
    </xs:element>
  </xs:schema>
  <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"
    xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <NewDataSet xmlns="">
      <Table diffgr:id="Table1" msdata:rowOrder="0">
        <id_subkurslokal>962545</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>16741.87</beli_subkurslokal>
        <jual_subkurslokal>16910.13</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-06T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>USD  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table2" msdata:rowOrder="1">
        <id_subkurslokal>962310</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>16691.13</beli_subkurslokal>
        <jual_subkurslokal>16858.88</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-05T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>USD  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table3" msdata:rowOrder="2">
        <id_subkurslokal>962075</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>16693.12</beli_subkurslokal>
        <jual_subkurslokal>16860.88</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-04T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>USD  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table4" msdata:rowOrder="3">
        <id_subkurslokal>961840</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>16716.00</beli_subkurslokal>
        <jual_subkurslokal>16884.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-03T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>USD  </mts_subkurslokal>
      </Table>
    </NewDataSet>
  </diffgr:diffgram>
</DataSet>"""

SAMPLE_BI_XML_EUR = b"""<?xml version="1.0" encoding="utf-8"?>
<DataSet xmlns="http://tempuri.org/">
  <xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
    <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
      <xs:complexType>
        <xs:choice minOccurs="0" maxOccurs="unbounded">
          <xs:element name="Table">
            <xs:complexType>
              <xs:sequence>
                <xs:element name="id_subkurslokal" type="xs:int" minOccurs="0" />
                <xs:element name="lnk_subkurslokal" type="xs:int" minOccurs="0" />
                <xs:element name="nil_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="beli_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="jual_subkurslokal" type="xs:decimal" minOccurs="0" />
                <xs:element name="tgl_subkurslokal" type="xs:dateTime" minOccurs="0" />
                <xs:element name="mts_subkurslokal" type="xs:string" minOccurs="0" />
              </xs:sequence>
            </xs:complexType>
          </xs:element>
        </xs:choice>
      </xs:complexType>
    </xs:element>
  </xs:schema>
  <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"
    xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <NewDataSet xmlns="">
      <Table diffgr:id="Table1" msdata:rowOrder="0">
        <id_subkurslokal>962550</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>17421.00</beli_subkurslokal>
        <jual_subkurslokal>17605.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-06T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>EUR  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table2" msdata:rowOrder="1">
        <id_subkurslokal>962315</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>17380.00</beli_subkurslokal>
        <jual_subkurslokal>17560.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-05T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>EUR  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table3" msdata:rowOrder="2">
        <id_subkurslokal>962080</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>17390.00</beli_subkurslokal>
        <jual_subkurslokal>17570.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-04T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>EUR  </mts_subkurslokal>
      </Table>
      <Table diffgr:id="Table4" msdata:rowOrder="3">
        <id_subkurslokal>961845</id_subkurslokal>
        <lnk_subkurslokal>44</lnk_subkurslokal>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>17400.00</beli_subkurslokal>
        <jual_subkurslokal>17580.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-03T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>EUR  </mts_subkurslokal>
      </Table>
    </NewDataSet>
  </diffgr:diffgram>
</DataSet>"""

# Sample with nil_subkurslokal=100 (e.g. JPY - quoted per 100 units)
SAMPLE_BI_XML_JPY_NIL100 = b"""<?xml version="1.0" encoding="utf-8"?>
<DataSet xmlns="http://tempuri.org/">
  <xs:schema id="NewDataSet" xmlns="" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:msdata="urn:schemas-microsoft-com:xml-msdata">
    <xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:UseCurrentLocale="true">
      <xs:complexType><xs:choice minOccurs="0" maxOccurs="unbounded">
        <xs:element name="Table"><xs:complexType><xs:sequence>
          <xs:element name="nil_subkurslokal" type="xs:decimal" minOccurs="0" />
          <xs:element name="beli_subkurslokal" type="xs:decimal" minOccurs="0" />
          <xs:element name="jual_subkurslokal" type="xs:decimal" minOccurs="0" />
          <xs:element name="tgl_subkurslokal" type="xs:dateTime" minOccurs="0" />
          <xs:element name="mts_subkurslokal" type="xs:string" minOccurs="0" />
        </xs:sequence></xs:complexType></xs:element>
      </xs:choice></xs:complexType>
    </xs:element></xs:schema>
  <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"
    xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <NewDataSet xmlns="">
      <Table diffgr:id="Table1" msdata:rowOrder="0">
        <nil_subkurslokal>100.00</nil_subkurslokal>
        <beli_subkurslokal>10700.00</beli_subkurslokal>
        <jual_subkurslokal>10900.00</jual_subkurslokal>
        <tgl_subkurslokal>2026-02-06T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>JPY  </mts_subkurslokal>
      </Table>
    </NewDataSet>
  </diffgr:diffgram>
</DataSet>"""


def _mock_urlopen(req, *args, **kwargs):
    """Mock urlopen returning sample BI XML based on currency code in URL."""
    url_str = req.full_url if hasattr(req, "full_url") else str(req)
    if "mts=USD" in url_str:
        return BytesIO(SAMPLE_BI_XML_USD)
    elif "mts=EUR" in url_str:
        return BytesIO(SAMPLE_BI_XML_EUR)
    elif "mts=JPY" in url_str:
        return BytesIO(SAMPLE_BI_XML_JPY_NIL100)
    return BytesIO(
        b'<?xml version="1.0" encoding="utf-8"?>'
        b'<DataSet xmlns="http://tempuri.org/"><diffgr:diffgram '
        b'xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
        b'<NewDataSet xmlns=""/></diffgr:diffgram></DataSet>'
    )


class TestResCurrencyRateProviderBI(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Company = cls.env["res.company"]
        cls.CurrencyRate = cls.env["res.currency.rate"]
        cls.CurrencyRateProvider = cls.env["res.currency.rate.provider"]

        cls.today = fields.Date.today()
        cls.idr_currency = cls.env.ref("base.IDR")
        cls.usd_currency = cls.env.ref("base.USD")
        cls.eur_currency = cls.env.ref("base.EUR")
        cls.jpy_currency = cls.env.ref("base.JPY")

        cls.company = cls.Company.create(
            {"name": "Test PT Indonesia", "currency_id": cls.idr_currency.id}
        )
        cls.env.user.company_ids += cls.company
        cls.env.company = cls.company

        cls.bi_provider = cls.CurrencyRateProvider.create(
            {
                "service": "BI",
                "currency_ids": [
                    (4, cls.usd_currency.id),
                    (4, cls.eur_currency.id),
                ],
            }
        )
        cls.CurrencyRate.search([]).unlink()

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen",
        side_effect=_mock_urlopen,
    )
    def test_scheduled_update(self, mock_urlopen):
        """Scheduled cron creates rates for USD and EUR."""
        self.bi_provider._scheduled_update()
        rates = self.CurrencyRate.search([("provider_id", "=", self.bi_provider.id)])
        currencies = rates.mapped("currency_id")
        self.assertIn(self.usd_currency, currencies)
        self.assertIn(self.eur_currency, currencies)

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen",
        side_effect=_mock_urlopen,
    )
    def test_wizard_update(self, mock_urlopen):
        """Wizard update creates rates for full date range (USD×4 + EUR×4 = 8)."""
        from datetime import date

        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, self.bi_provider.ids)])
            .create(
                {
                    "date_from": date(2026, 2, 3),
                    "date_to": date(2026, 2, 6),
                }
            )
        )
        wizard.action_update()
        rates = self.CurrencyRate.search([("provider_id", "=", self.bi_provider.id)])
        self.assertEqual(len(rates), 8)

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen",
        side_effect=_mock_urlopen,
    )
    def test_rate_value_idr_base(self, mock_urlopen):
        """Rate for USD on 2026-02-06: (16741.87+16910.13)/2 = 16826.0 IDR/USD.
        Stored in Odoo as 1/16826.0 (foreign per 1 IDR base).
        """
        from datetime import date

        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, self.bi_provider.ids)])
            .create(
                {
                    "date_from": date(2026, 2, 6),
                    "date_to": date(2026, 2, 6),
                }
            )
        )
        wizard.action_update()

        usd_rate = self.CurrencyRate.search(
            [
                ("provider_id", "=", self.bi_provider.id),
                ("currency_id", "=", self.usd_currency.id),
                ("name", "=", date(2026, 2, 6)),
            ],
            limit=1,
        )
        self.assertTrue(usd_rate, "USD rate for 2026-02-06 should exist")
        # (16741.87 + 16910.13) / 2 = 16826.0 IDR/USD → stored as 1/16826
        expected_rate = 1 / 16826.0
        self.assertAlmostEqual(usd_rate.rate, expected_rate, places=10)

    def test_parse_bi_response_usd(self):
        """Parse real-format XML: 4 USD rows returned correctly."""
        rates = self.bi_provider._parse_bi_response(SAMPLE_BI_XML_USD, "USD")
        self.assertEqual(len(rates), 4)
        self.assertIn("2026-02-03", rates)
        self.assertIn("2026-02-04", rates)
        self.assertIn("2026-02-05", rates)
        self.assertIn("2026-02-06", rates)
        # 2026-02-06: (16741.87 + 16910.13) / 2 / 1 = 16826.0
        self.assertAlmostEqual(rates["2026-02-06"], 16826.0)
        # 2026-02-03: (16716.00 + 16884.00) / 2 / 1 = 16800.0
        self.assertAlmostEqual(rates["2026-02-03"], 16800.0)

    def test_parse_bi_response_nil100(self):
        """nil_subkurslokal=100: rate normalized to per-1-unit.
        JPY: (10700 + 10900) / 2 / 100 = 108.0 IDR/JPY
        """
        rates = self.bi_provider._parse_bi_response(SAMPLE_BI_XML_JPY_NIL100, "JPY")
        self.assertEqual(len(rates), 1)
        self.assertAlmostEqual(rates["2026-02-06"], 108.0)

    def test_parse_bi_response_empty(self):
        """Empty DataSet returns empty dict without raising."""
        empty_xml = (
            b'<?xml version="1.0" encoding="utf-8"?>'
            b'<DataSet xmlns="http://tempuri.org/">'
            b'<diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">'
            b'<NewDataSet xmlns=""/>'
            b"</diffgr:diffgram></DataSet>"
        )
        rates = self.bi_provider._parse_bi_response(empty_xml, "USD")
        self.assertEqual(rates, {})

    def test_supported_currencies(self):
        """BI provider returns correct supported currencies list."""
        currencies = self.bi_provider._get_supported_currencies()
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)
        self.assertIn("JPY", currencies)
        self.assertIn("SGD", currencies)
        self.assertIn("MYR", currencies)
        self.assertNotIn("IDR", currencies)

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen",
        side_effect=_mock_urlopen,
    )
    def test_foreign_base_currency_cross_rate(self, mock_urlopen):
        """Test cross-rate calculation for foreign base currency (USD base)."""
        from datetime import date

        # Create USD-based company
        usd_company = self.Company.create(
            {"name": "Test US Company", "currency_id": self.usd_currency.id}
        )
        bi_provider_usd = self.CurrencyRateProvider.with_company(usd_company).create(
            {
                "service": "BI",
                "currency_ids": [(4, self.eur_currency.id)],
                "company_id": usd_company.id,
            }
        )

        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, bi_provider_usd.ids)])
            .with_company(usd_company)
            .create(
                {
                    "date_from": date(2026, 2, 6),
                    "date_to": date(2026, 2, 6),
                }
            )
        )
        wizard.action_update()

        eur_rate = self.CurrencyRate.search(
            [
                ("provider_id", "=", bi_provider_usd.id),
                ("currency_id", "=", self.eur_currency.id),
                ("name", "=", date(2026, 2, 6)),
            ],
            limit=1,
        )
        self.assertTrue(eur_rate, "EUR rate for USD base should exist")
        # Cross rate: EUR/USD = IDR/USD ÷ IDR/EUR = 16826 ÷ 17513 ≈ 0.9608
        # IDR/USD = (16741.87 + 16910.13) / 2 = 16826
        # IDR/EUR = (17421 + 17605) / 2 = 17513
        expected_cross_rate = 16826.0 / 17513.0
        self.assertAlmostEqual(eur_rate.rate, expected_cross_rate, places=4)

    def test_unsupported_base_currency(self):
        """Test error when base currency not supported by BI."""
        from datetime import date

        from odoo.exceptions import UserError

        # BRL (Brazilian Real) is not in BI_SUPPORTED_CURRENCIES
        brl_currency = self.env.ref("base.BRL")
        brl_company = self.Company.create(
            {"name": "Test Brazil Company", "currency_id": brl_currency.id}
        )
        bi_provider_brl = self.CurrencyRateProvider.with_company(brl_company).create(
            {
                "service": "BI",
                "currency_ids": [(4, self.usd_currency.id)],
                "company_id": brl_company.id,
            }
        )

        with self.assertRaises(UserError) as cm:
            bi_provider_brl._obtain_rates(
                "BRL", ["USD"], date(2026, 2, 6), date(2026, 2, 6)
            )
        self.assertIn("not supported", str(cm.exception))

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen"
    )
    def test_connection_error(self, mock_urlopen):
        """Test handling of connection error."""
        from datetime import date
        from urllib.error import URLError

        from odoo.exceptions import UserError

        mock_urlopen.side_effect = URLError("Connection timeout")

        with self.assertRaises(UserError) as cm:
            self.bi_provider._obtain_rates(
                "IDR", ["USD"], date(2026, 2, 6), date(2026, 2, 6)
            )
        self.assertIn("Cannot connect", str(cm.exception))

    def test_parse_missing_fields(self):
        """Test parsing XML with missing beli/jual fields."""
        missing_fields_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<DataSet xmlns="http://tempuri.org/">
  <diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <NewDataSet xmlns="">
      <Table>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <tgl_subkurslokal>2026-02-06T00:00:00+07:00</tgl_subkurslokal>
        <mts_subkurslokal>USD</mts_subkurslokal>
      </Table>
    </NewDataSet>
  </diffgr:diffgram>
</DataSet>"""
        rates = self.bi_provider._parse_bi_response(missing_fields_xml, "USD")
        self.assertEqual(rates, {})

    def test_parse_invalid_xml(self):
        """Test parsing invalid XML returns empty dict."""
        invalid_xml = b"<invalid>xml"
        rates = self.bi_provider._parse_bi_response(invalid_xml, "USD")
        self.assertEqual(rates, {})

    def test_parse_missing_date(self):
        """Test parsing XML with missing date field."""
        missing_date_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<DataSet xmlns="http://tempuri.org/">
  <diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <NewDataSet xmlns="">
      <Table>
        <nil_subkurslokal>1.00</nil_subkurslokal>
        <beli_subkurslokal>16741.87</beli_subkurslokal>
        <jual_subkurslokal>16910.13</jual_subkurslokal>
        <mts_subkurslokal>USD</mts_subkurslokal>
      </Table>
    </NewDataSet>
  </diffgr:diffgram>
</DataSet>"""
        rates = self.bi_provider._parse_bi_response(missing_date_xml, "USD")
        self.assertEqual(rates, {})

    def test_get_currencies_to_fetch_idr_base(self):
        """Test _get_currencies_to_fetch with IDR base."""
        fetch = self.bi_provider._get_currencies_to_fetch("IDR", ["USD", "EUR", "GBP"])
        self.assertIn("USD", fetch)
        self.assertIn("EUR", fetch)
        self.assertIn("GBP", fetch)
        self.assertNotIn("IDR", fetch)

    def test_get_currencies_to_fetch_foreign_base(self):
        """Test _get_currencies_to_fetch with USD base adds USD to fetch list."""
        fetch = self.bi_provider._get_currencies_to_fetch("USD", ["EUR", "GBP"])
        self.assertIn("USD", fetch)  # Added for cross-rate calculation
        self.assertIn("EUR", fetch)
        self.assertIn("GBP", fetch)

    def test_convert_idr_base_rates(self):
        """Test _convert_idr_base_rates returns inverted format."""
        rates_by_date = {"2026-02-06": {"USD": 16826.0}}
        result = self.bi_provider._convert_idr_base_rates(rates_by_date)
        self.assertEqual(result["2026-02-06"]["USD"], {"inverted": 16826.0})

    def test_convert_foreign_base_rates(self):
        """Test _convert_foreign_base_rates calculates cross rates."""
        rates_by_date = {"2026-02-06": {"USD": 16826.0, "EUR": 17513.0}}
        result = self.bi_provider._convert_foreign_base_rates(rates_by_date, "USD")
        # EUR/USD = 16826 / 17513
        expected = 16826.0 / 17513.0
        self.assertAlmostEqual(result["2026-02-06"]["EUR"], expected, places=4)

    def test_convert_foreign_base_rates_missing_base(self):
        """Test _convert_foreign_base_rates skips dates without base currency."""
        rates_by_date = {
            "2026-02-06": {"EUR": 17513.0},  # Missing USD
            "2026-02-07": {"USD": 16826.0, "EUR": 17513.0},
        }
        result = self.bi_provider._convert_foreign_base_rates(rates_by_date, "USD")
        self.assertNotIn("2026-02-06", result)  # Skipped
        self.assertIn("2026-02-07", result)

    @patch(
        "odoo.addons.currency_rate_update_BI.models"
        ".res_currency_rate_provider_BI.urlopen",
        side_effect=_mock_urlopen,
    )
    def test_foreign_base_with_idr_selected(self, mock_urlopen):
        """Test that IDR can be selected and has correct rate when base is USD."""
        from datetime import date

        # Create USD-based company
        usd_company = self.Company.create(
            {"name": "Test US Company IDR", "currency_id": self.usd_currency.id}
        )

        bi_provider_usd = self.CurrencyRateProvider.with_company(usd_company).create(
            {
                "service": "BI",
                "currency_ids": [
                    (4, self.idr_currency.id),
                    (4, self.eur_currency.id),
                ],
                "company_id": usd_company.id,
            }
        )

        wizard = (
            self.env["res.currency.rate.update.wizard"]
            .with_context(default_provider_ids=[(6, False, bi_provider_usd.ids)])
            .with_company(usd_company)
            .create(
                {
                    "date_from": date(2026, 2, 6),
                    "date_to": date(2026, 2, 6),
                }
            )
        )
        wizard.action_update()

        # Check IDR rate was created
        idr_rate = self.CurrencyRate.search(
            [
                ("provider_id", "=", bi_provider_usd.id),
                ("currency_id", "=", self.idr_currency.id),
                ("name", "=", date(2026, 2, 6)),
            ],
            limit=1,
        )
        self.assertTrue(idr_rate, "IDR rate for USD base should exist")

        # IDR/USD rate from BI: (16741.87 + 16910.13) / 2 = 16826.0
        expected_rate = 16826.0
        self.assertAlmostEqual(idr_rate.rate, expected_rate, places=1)

        # Also verify EUR cross-rate still works
        eur_rate = self.CurrencyRate.search(
            [
                ("provider_id", "=", bi_provider_usd.id),
                ("currency_id", "=", self.eur_currency.id),
                ("name", "=", date(2026, 2, 6)),
            ],
            limit=1,
        )
        self.assertTrue(eur_rate, "EUR rate should also exist")
        expected_eur_rate = 16826.0 / 17513.0
        self.assertAlmostEqual(eur_rate.rate, expected_eur_rate, places=4)

    def test_supported_currencies_idr_base(self):
        """Test that IDR is NOT in supported currencies when base is IDR."""
        currencies = self.bi_provider._get_supported_currencies()
        self.assertNotIn("IDR", currencies)

    def test_supported_currencies_usd_base(self):
        """Test that IDR IS in supported currencies when base is USD."""
        usd_company = self.Company.create(
            {"name": "Test US Company", "currency_id": self.usd_currency.id}
        )
        bi_provider_usd = self.CurrencyRateProvider.with_company(usd_company).create(
            {
                "service": "BI",
                "currency_ids": [],
                "company_id": usd_company.id,
            }
        )
        currencies = bi_provider_usd._get_supported_currencies()
        self.assertIn("IDR", currencies)
        self.assertIn("USD", currencies)
        self.assertIn("EUR", currencies)
