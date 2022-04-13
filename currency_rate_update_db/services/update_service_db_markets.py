# © 2022 sewisoft
# © 2009 Camptocamp
# © 2009 Grzegorz Grzelak
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterInterface

from lxml import etree
from datetime import datetime, date

import logging

_logger = logging.getLogger(__name__)


class DBMGetter(CurrencyGetterInterface):
    """Implementation of Currency_getter_factory interface
    for DB-Markets service
    """
    code = 'DBM1ASK'
    name = _('DB-Markets 1pm ask rate')  # Deutsche Bank 13Uhr Geldkurs
    url = 'https://www.db-markets.com/dbm/portal/FxSettlementRates/'
    rate_type = 'ask'
    supported_currency_array = [
        'AED', 'AUD', 'BGN', 'BHD', 'CAD', 'CHF', 'CNH', 'CZK', 'DKK', 'GBP',
        'HKD', 'HRK', 'HUF', 'ILS', 'INR', 'JOD', 'JPY', 'KES', 'KWD', 'LKR',
        'MAD', 'MUR', 'MXN', 'NOK', 'NZD', 'OMR', 'PKR', 'PLN', 'QAR', 'RON',
        'RSD', 'RUB', 'SAR', 'SEK', 'SGD', 'THB', 'TND', 'TRY', 'USD', 'ZAR',
    ]

    def rate_retrieve(self, dom, curr):
        """Parse a dom node to retrieve-
        currencies data

        """
        res = {}
        xpath_curr_rate = ("/Envelope/Cube/Cube/"
                           "Cube[@currency='%s']/@" + self.rate_type) % (curr.upper())
        res['rate_currency'] = float(
            dom.xpath(xpath_curr_rate)[0]
        )
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        """implementation of abstract method of Curreny_getter_interface"""
        url = self.url + date.today().strftime("%d-%m-%Y")

        # We do not want to update the main currency
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        _logger.debug("DBM currency rate service : connecting...")
        rawfile = self.get_url(url)
        dom = etree.fromstring(rawfile)
        _logger.debug("DBM sent a valid XML file")
        rate_date = dom.xpath('/Envelope/Cube/Cube/@time')[0]
        rate_date_datetime = datetime.strptime(rate_date, '%d.%m.%y')
        self.check_rate_date(rate_date_datetime, max_delta_days)
        # We dynamically update supported currencies
        self.supported_currency_array = dom.xpath(
            "/Envelope/Cube/Cube/Cube/@currency"
        )
        self.supported_currency_array.append('EUR')
        _logger.debug("Supported currencies = %s " %
                      self.supported_currency_array)
        self.validate_cur(main_currency)
        if main_currency != 'EUR':
            main_curr_data = self.rate_retrieve(dom, main_currency)
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'EUR':
                rate = 1 / main_curr_data['rate_currency']
            else:
                curr_data = self.rate_retrieve(dom, curr)
                if main_currency == 'EUR':
                    rate = curr_data['rate_currency']
                else:
                    rate = (curr_data['rate_currency'] /
                            main_curr_data['rate_currency'])
            self.updated_currency[curr] = rate
            _logger.debug(
                "Rate retrieved : 1 %s = %s %s" % (main_currency, rate, curr)
            )
        return self.updated_currency, self.log_info


class DBMGetterBid(DBMGetter):
    """Implementation of Currency_getter_factory interface
    for DB-Markets service
    """
    code = 'DBM1BID'
    name = _('DB-Markets 1pm bid rate')  # Deutsche Bank 13Uhr Briefkurs
    url = 'https://www.db-markets.com/dbm/portal/FxSettlementRates/'
    rate_type = 'bid'


class DBMGetter6(DBMGetter):
    """Implementation of Currency_getter_factory interface
    for DB-Markets service
    """
    code = 'DBM6ASK'
    name = _('DB-Markets 6pm ask rate')  # Deutsche Bank 18Uhr Geldkurs
    url = 'https://www.db-markets.com/dbm/portal/FxSettlementRates6/'
    rate_type = 'ask'


class DBMGetter6Bid(DBMGetter):
    """Implementation of Currency_getter_factory interface
    for DB-Markets service
    """
    code = 'DBM6BID'
    name = _('DB-Markets 6pm bid rate')  # Deutsche Bank 18Uhr Briefkurs
    url = 'https://www.db-markets.com/dbm/portal/FxSettlementRates6/'
    rate_type = 'bid'
