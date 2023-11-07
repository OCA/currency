# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from lxml import etree
from datetime import datetime, timedelta
from collections import defaultdict
import pytz

MONEDAS={'EUR':'euro','CNY':'yuan','TRY':'lira','RUB':'rublo','USD':'dolar'}
CARACAS_TZ = pytz.timezone('America/Caracas') ## se necesita porque la hora de bcv es de vzla

class ResCompany(models.Model):
    _inherit = "res.currency.rate.provider"
    service = fields.Selection(
        selection_add=[('bcv','BCV scrapping')],
        ondelete={"bcv": "set default"},
        default='bcv')

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "bcv":
            return super()._get_supported_currencies()
        return list(MONEDAS.keys())

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "bcv":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )

        content = defaultdict(dict)

        bcv_data = self._scrap(currencies)

        for k in bcv_data.keys():
            dt = bcv_data[k][1].isoformat()
            content[dt][k]=bcv_data[k][0]

        return content

    def _scrap(self, available_currencies):

        request_url = 'http://www.bcv.org.ve/'

        try:
            fetched_data = requests.get(request_url,verify=False)
        except:
            return False

        rslt = {}

        available_currency_names = available_currencies

        htmlelem = etree.fromstring(fetched_data.content, etree.HTMLParser())

        dt=datetime.now(CARACAS_TZ)
        for currency_name in available_currency_names:
            try:

                if currency_name in ['Bs','VES','VEF','VED']:
                    rslt[currency_name]=(1.0,dt)
                else:
                    sValue=htmlelem.xpath(f".//div[@id='{MONEDAS[currency_name]}']/div/div/div[2]/strong")[0].text
                    value=float(sValue.replace(' ', '').replace(",", "."))

                    rslt[currency_name] = (1.0/value,dt)
            except:
                pass

        return rslt
