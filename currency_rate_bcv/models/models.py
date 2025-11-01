import logging
from collections import defaultdict
from datetime import datetime

import pytz
import requests
from lxml import etree

from odoo import fields, models

_logger = logging.getLogger(__name__)

TIMEOUT = 5000
REQUEST_URL = "http://www.bcv.org.ve/"
XPATH_MAPPING_CURRENCIES = {
    "EUR": "euro",
    "CNY": "yuan",
    "TRY": "lira",
    "RUB": "rublo",
    "USD": "dolar",
}
CARACAS_TZ = pytz.timezone("America/Caracas")


class ResCompany(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("bcv", "Banco Central de Venezuela (BCV)")],
        ondelete={"bcv": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "bcv":
            return super()._get_supported_currencies()
        return list(XPATH_MAPPING_CURRENCIES.keys())

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "bcv":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)

        content = defaultdict(dict)

        bcv_data = self._scrap(currencies)

        for k, v in bcv_data.items():
            dt = v[1].isoformat()
            content[dt][k] = v[0]

        return content

    def _scrap(self, available_currencies):
        rslt = {}
        try:
            fetched_data = requests.get(REQUEST_URL, verify=False, timeout=TIMEOUT)
        except Exception as e:
            _logger.debug("%s, %s", self._name, e)
            return rslt

        available_currency_names = available_currencies
        htmlelem = etree.fromstring(fetched_data.content, etree.HTMLParser())
        dt = datetime.now(CARACAS_TZ)

        currency_ve_ids = self.env.ref(
            "base.VES", raise_if_not_found=False
        ) + self.env.ref("base.VEF", raise_if_not_found=False)

        for currency_name in available_currency_names:
            try:
                if currency_name in currency_ve_ids.mapped("name"):
                    rslt[currency_name] = (1.0, dt)
                else:
                    sValue = htmlelem.xpath(
                        f".//div[@id='{XPATH_MAPPING_CURRENCIES[currency_name]}']/div/div/div[2]/strong"
                    )[0].text
                    value = float(sValue.replace(" ", "").replace(",", "."))

                    rslt[currency_name] = (1.0 / value, dt)
            except Exception as e:
                _logger.debug("%s, %s", self._name, e)

        return rslt
