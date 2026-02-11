# Copyright 2026 PT Solusi Aglis Indonesia (http://solusiaglis.co.id)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from urllib.error import URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Bank Indonesia SOAP Webservice (HTTP GET style)
# Source: https://www.bi.go.id/biwebservice/wskursbi.asmx
BI_WEBSERVICE_URL = (
    "https://www.bi.go.id/biwebservice/wskursbi.asmx/getSubKursLokal3"
    "?mts={currency}&startdate={date_from}&enddate={date_to}"
)

# BI server requires browser-like headers, otherwise returns empty response
BI_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
}

# Currencies published by Bank Indonesia in Kurs Transaksi BI
# Source: https://www.bi.go.id/en/statistik/informasi-kurs/transaksi-bi/
BI_SUPPORTED_CURRENCIES = [
    "USD",  # US Dollar
    "EUR",  # Euro
    "GBP",  # British Pound
    "JPY",  # Japanese Yen
    "SGD",  # Singapore Dollar
    "AUD",  # Australian Dollar
    "BND",  # Brunei Dollar
    "CAD",  # Canadian Dollar
    "CHF",  # Swiss Franc
    "CNY",  # Chinese Yuan
    "DKK",  # Danish Krone
    "HKD",  # Hong Kong Dollar
    "KRW",  # South Korean Won
    "MYR",  # Malaysian Ringgit
    "NOK",  # Norwegian Krone
    "NZD",  # New Zealand Dollar
    "SAR",  # Saudi Riyal
    "SEK",  # Swedish Krona
    "THB",  # Thai Baht
]


class ResCurrencyRateProviderBI(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("BI", "Bank Indonesia (Kurs Transaksi)")],
        ondelete={"BI": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "BI":
            return super()._get_supported_currencies()
        return BI_SUPPORTED_CURRENCIES

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "BI":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)

        # Determine which currencies to fetch from BI
        fetch_currencies = self._get_currencies_to_fetch(base_currency, currencies)
        if not fetch_currencies:
            return {}

        # Fetch rates from BI webservice
        rates_by_date = self._fetch_bi_rates(fetch_currencies, date_from, date_to)
        if not rates_by_date:
            return {}

        # Convert to Odoo format based on base currency
        return self._convert_bi_rates_to_odoo(rates_by_date, base_currency)

    def _get_currencies_to_fetch(self, base_currency, currencies):
        """Determine which currencies need to be fetched from BI."""
        fetch_currencies = [c for c in currencies if c in BI_SUPPORTED_CURRENCIES]
        # If company base is not IDR but is in BI's list, we need it for cross-rate calc
        if base_currency in BI_SUPPORTED_CURRENCIES and base_currency != "IDR":
            if base_currency not in fetch_currencies:
                fetch_currencies.append(base_currency)
        return fetch_currencies

    def _fetch_bi_rates(self, fetch_currencies, date_from, date_to):
        """Fetch exchange rates from BI webservice for given currencies."""
        rates_by_date = {}
        for currency in fetch_currencies:
            url = BI_WEBSERVICE_URL.format(
                currency=currency,
                date_from=date_from.strftime("%Y-%m-%d"),
                date_to=date_to.strftime("%Y-%m-%d"),
            )
            try:
                req = Request(url, headers=BI_REQUEST_HEADERS)
                with urlopen(req, timeout=30) as response:
                    xml_data = response.read()
                    currency_rates = self._parse_bi_response(xml_data, currency)
                    for date_str, rate_value in currency_rates.items():
                        if date_str not in rates_by_date:
                            rates_by_date[date_str] = {}
                        rates_by_date[date_str][currency] = rate_value
            except URLError as e:
                _logger.warning(
                    "Currency Rate Provider BI: Failed to fetch %s rates from BI: %s",
                    currency,
                    str(e),
                )
                raise UserError(
                    _(
                        "Cannot connect to Bank Indonesia webservice.\n"
                        "Please check your internet connection.\n"
                        "URL: %(url)s\nError: %(error)s"
                    )
                    % {"url": url, "error": str(e)}
                ) from e
        return rates_by_date

    def _convert_bi_rates_to_odoo(self, rates_by_date, base_currency):
        """Convert BI rates to Odoo format based on base currency.

        BI publishes: X IDR per 1 foreign currency (e.g. 16826 IDR/USD)
        Odoo _process_rate expects: {"inverted": X} where X = IDR per 1 foreign
        _process_rate will compute: direct = 1/X (foreign per 1 IDR, used as rate)
        """
        if base_currency == "IDR":
            return self._convert_idr_base_rates(rates_by_date)
        elif base_currency in BI_SUPPORTED_CURRENCIES:
            return self._convert_foreign_base_rates(rates_by_date, base_currency)
        else:
            raise UserError(
                _(
                    "Bank Indonesia provider: Company base currency %(currency)s "
                    "is not supported. BI supports IDR as base or any of: %(list)s"
                )
                % {
                    "currency": base_currency,
                    "list": ", ".join(BI_SUPPORTED_CURRENCIES),
                }
            )

    def _convert_idr_base_rates(self, rates_by_date):
        """Convert rates for IDR base currency."""
        content = {}
        for date_str, rates in rates_by_date.items():
            content[date_str] = {}
            for curr, rate_idr in rates.items():
                # rate_idr = IDR per 1 unit of `curr` (e.g. 16826 for USD)
                # Odoo stores "foreign per 1 base" => rate_usd = 1/16826
                # We pass {"inverted": 16826} so _process_rate computes 1/16826
                content[date_str][curr] = {"inverted": rate_idr}
        return content

    def _convert_foreign_base_rates(self, rates_by_date, base_currency):
        """Convert rates for foreign base currency using cross-rates."""
        content = {}
        for date_str, rates in rates_by_date.items():
            if base_currency not in rates:
                # Skip dates where base currency rate is missing
                continue
            base_idr = rates[base_currency]  # IDR per 1 base currency
            content[date_str] = {}
            for curr, rate_idr in rates.items():
                if curr == base_currency:
                    continue
                # Cross rate: foreign per 1 base = (IDR/base) / (IDR/foreign)
                # = rate_idr_base / rate_idr_foreign
                # e.g. EUR/USD = (IDR/USD) / (IDR/EUR) = 16826 / 18500 ≈ 0.9095
                cross_rate = base_idr / rate_idr
                content[date_str][curr] = cross_rate
        return content

    def _parse_bi_response(self, xml_data, expected_currency):
        """Parse BI SOAP DataSet XML response (diffgram format).

        BI's wsKursBI (getSubKursLokal3) returns a Microsoft ADO.NET DataSet
        XML in diffgram format. Actual structure:

            <DataSet xmlns="http://tempuri.org/">
              <xs:schema>...</xs:schema>
              <diffgr:diffgram xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
                <NewDataSet>
                  <Table diffgr:id="Table1" msdata:rowOrder="0">
                    <id_subkurslokal>962545</id_subkurslokal>
                    <nil_subkurslokal>1.00</nil_subkurslokal>
                    <beli_subkurslokal>16741.87</beli_subkurslokal>
                    <jual_subkurslokal>16910.13</jual_subkurslokal>
                    <tgl_subkurslokal>2026-02-06T00:00:00+07:00</tgl_subkurslokal>
                    <mts_subkurslokal>USD  </mts_subkurslokal>
                  </Table>
                  ...
                </NewDataSet>
              </diffgr:diffgram>
            </DataSet>

        Notes:
        - No kurs_tengah; rate = (beli + jual) / 2
        - nil_subkurslokal is the nominal unit (1 for USD, may be 100 for JPY)
        - mts_subkurslokal has trailing spaces
        - Rate stored = (beli + jual) / 2 / nil_subkurslokal

        Returns dict: {date_str: idr_per_1_foreign_unit}
        """
        result = {}
        try:
            root = ElementTree.fromstring(xml_data)
        except ElementTree.ParseError as e:
            _logger.error("BI: Failed to parse XML response: %s", str(e))
            return result

        # Strip all XML namespaces for simpler XPath queries
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]
            # Also strip namespaced attributes (e.g. diffgr:id)
            elem.attrib = {
                k.split("}", 1)[1] if "}" in k else k: v for k, v in elem.attrib.items()
            }

        # Data lives inside diffgram > NewDataSet > Table
        for table in root.findall(".//NewDataSet/Table"):
            date_str = self._get_bi_date(table)
            if not date_str:
                continue

            rate_value = self._get_bi_rate(table)
            if rate_value is None:
                continue

            result[date_str] = rate_value

        if not result:
            _logger.warning(
                "BI: No exchange rate data found for %s in XML response. "
                "The webservice may not have data for the requested date range, "
                "or the XML structure may have changed.",
                expected_currency,
            )
        return result

    def _get_bi_date(self, table_element):
        """Extract and normalize date from a BI Table element.

        BI returns dates as ISO 8601 with timezone:
        e.g. "2026-02-06T00:00:00+07:00"

        Returns date string "YYYY-MM-DD" or None if not found.
        """
        el = table_element.find("tgl_subkurslokal")
        if el is not None and el.text:
            return el.text.strip().split("T")[0]
        return None

    def _get_bi_rate(self, table_element):
        """Extract exchange rate (IDR per 1 foreign currency unit) from Table.

        BI Kurs Transaksi publishes beli (buy) and jual (sell) rates only.
        Middle rate = (beli + jual) / 2.

        nil_subkurslokal is the nominal unit. For most currencies it is 1,
        but some currencies (e.g. JPY, KRW) may use 100 as the unit, meaning
        the listed rate is per 100 units. We divide by nil to normalize to
        rate per 1 unit.

        Returns float IDR-per-1-foreign-unit, or None on error.
        """
        beli_el = table_element.find("beli_subkurslokal")
        jual_el = table_element.find("jual_subkurslokal")
        nil_el = table_element.find("nil_subkurslokal")

        if not (
            beli_el is not None
            and beli_el.text
            and jual_el is not None
            and jual_el.text
        ):
            _logger.warning(
                "BI: Could not extract rate from Table element. " "Available tags: %s",
                [child.tag for child in table_element],
            )
            return None

        try:
            beli = float(beli_el.text.strip().replace(",", ""))
            jual = float(jual_el.text.strip().replace(",", ""))
            nil = (
                float(nil_el.text.strip())
                if nil_el is not None and nil_el.text
                else 1.0
            )
            if nil <= 0:
                nil = 1.0
            return (beli + jual) / 2 / nil
        except (ValueError, ZeroDivisionError):
            return None
