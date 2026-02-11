Adds **Bank Indonesia (BI)** as a currency rates provider for the
``currency_rate_update`` module. Exchange rates are fetched from
Bank Indonesia's official SOAP webservice (wsKursBI) using the
``getSubKursLokal3`` method.

**Data Source:** Bank Indonesia — https://www.bi.go.id

**Rate Type:** Kurs Transaksi BI (Transaction Rates — middle rate / kurs tengah)

**Update Frequency:** Daily on business days (Mon–Fri, excluding Indonesian national holidays)

**Supported Currencies (vs IDR):**

+-----+----------------------------+
| USD | United States Dollar       |
+-----+----------------------------+
| EUR | Euro                       |
+-----+----------------------------+
| GBP | British Pound              |
+-----+----------------------------+
| JPY | Japanese Yen               |
+-----+----------------------------+
| SGD | Singapore Dollar           |
+-----+----------------------------+
| AUD | Australian Dollar          |
+-----+----------------------------+
| BND | Brunei Dollar              |
+-----+----------------------------+
| CAD | Canadian Dollar            |
+-----+----------------------------+
| CHF | Swiss Franc                |
+-----+----------------------------+
| CNY | Chinese Yuan               |
+-----+----------------------------+
| DKK | Danish Krone               |
+-----+----------------------------+
| HKD | Hong Kong Dollar           |
+-----+----------------------------+
| KRW | South Korean Won           |
+-----+----------------------------+
| MYR | Malaysian Ringgit          |
+-----+----------------------------+
| NOK | Norwegian Krone            |
+-----+----------------------------+
| NZD | New Zealand Dollar         |
+-----+----------------------------+
| SAR | Saudi Riyal                |
+-----+----------------------------+
| SEK | Swedish Krona              |
+-----+----------------------------+
| THB | Thai Baht                  |
+-----+----------------------------+

**Note:** This module is designed primarily for Indonesian companies
using **IDR (Indonesian Rupiah)** as their base currency. Cross-rate
calculations (e.g. USD base company wanting EUR rates) are supported
as long as the base currency is in the list above.
