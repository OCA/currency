import urllib.request
import xml.etree.ElementTree as ET

from odoo import fields, models


class ResCurrencyRateProviderECB(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("VCB", "Vietcombank")],
        ondelete={"VCB": "set default"},
        default="VCB",
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "VCB":
            return super()._get_supported_currencies()

        # List of currencies obrained from:
        # https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=68
        return [
            "AUD",
            "CAD",
            "CHF",
            "CNY",
            "DKK",
            "EUR",
            "GBP",
            "HKD",
            "INR",
            "JPY",
            "KRW",
            "KWD",
            "MYR",
            "NOK",
            "RUB",
            "SAR",
            "SEK",
            "SGD",
            "THB",
            "USD",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "VCB":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        lst_currencies = self._get_supported_currencies()
        invert_calculation = False
        if base_currency != "VND":
            invert_calculation = True
            if base_currency not in currencies:
                currencies.append(base_currency)

        # Depending on the date range, different URLs are used
        url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx?b=68"

        response = urllib.request.urlopen(url).read()
        root = ET.fromstring(response)
        content = {date_to: {}}
        for child in root:
            CurrencyCode = dict(child.attrib).get("CurrencyCode")
            if CurrencyCode not in lst_currencies or CurrencyCode not in currencies:
                continue
            rate = dict(child.attrib).get("Transfer")
            content[date_to].update({CurrencyCode: rate.replace(",", "")})

        if invert_calculation:
            for k in content.keys():
                base_rate = float(content[k][base_currency])
                for rate in content[k].keys():
                    content[k][rate] = str(float(content[k][rate]) / base_rate)
                content[k]["EUR"] = str(1.0 / base_rate)
        return content
