from ast import literal_eval
from odoo import _
from odoo.exceptions import UserError
from odoo.addons.currency_rate_update.services.currency_getter_interface \
    import CurrencyGetterInterface
import logging
_logger = logging.getLogger(__name__)


class FCCAAdminGetter(CurrencyGetterInterface):

    code = 'FCCA'
    name = 'Free Currency Converter API'
    service_parameters = ['free_currencyconverter_api']

    allowed_base_currencies = [
        'BND', 'BYR', 'TZS', 'CLP', 'BWP', 'PYG', 'SHP', 'SLL', 'MGA', 'LKR',
        'BDT', 'GHS', 'ANG', 'CDF', 'KRW', 'KZT', 'HRK', 'BTN', 'NPR', 'QAR',
        'TND', 'TJS', 'BIF', 'ISK', 'KYD', 'HKD', 'BYN', 'YER', 'PLN', 'GBP',
        'XCD', 'MKD', 'AZN', 'XPF', 'RUB', 'XAF', 'TRY', 'BAM', 'AUD', 'SOS',
        'INR', 'IQD', 'MXN', 'RWF', 'KES', 'AFN', 'LBP', 'LVL', 'MAD', 'SDG',
        'DZD', 'CHF', 'ZAR', 'TWD', 'DKK', 'LRD', 'AMD', 'KHR', 'VUV', 'DOP',
        'IDR', 'DJF', 'VND', 'MOP', 'KGS', 'XDR', 'LAK', 'ERN', 'MDL', 'MYR',
        'NIO', 'VEF', 'BHD', 'PKR', 'SAR', 'ILS', 'ETB', 'GYD', 'CRC', 'MVR',
        'SZL', 'SBD', 'LSL', 'BZD', 'GIP', 'SYP', 'MNT', 'EGP', 'MRO', 'EUR',
        'CVE', 'BRL', 'GNF', 'KPW', 'NAD', 'HTG', 'UZS', 'MMK', 'KMF', 'GEL',
        'MZN', 'GMD', 'HUF', 'LYD', 'OMR', 'NZD', 'FJD', 'RON', 'SGD', 'BBD',
        'AWG', 'BGN', 'GTQ', 'MUR', 'NOK', 'JPY', 'JOD', 'MWK', 'JMD', 'TOP',
        'CZK', 'CAD', 'ALL', 'ARS', 'COP', 'CUP', 'RSD', 'XOF', 'SCR', 'CNY',
        'USD', 'HNL', 'TTD', 'THB', 'NGN', 'UAH', 'TMT', 'AOA', 'IRR', 'BOB',
        'SEK', 'PGK', 'PEN', 'SRD', 'BSD', 'KWD', 'UGX', 'PAB', 'UYU', 'ZMW',
        'WST', 'PHP', 'FKP', 'AED', 'BTC', 'STD']

    supported_currency_array = [
        'BND', 'BYR', 'TZS', 'CLP', 'BWP', 'PYG', 'SHP', 'SLL', 'MGA', 'LKR',
        'BDT', 'GHS', 'ANG', 'CDF', 'KRW', 'KZT', 'HRK', 'BTN', 'NPR', 'QAR',
        'TND', 'TJS', 'BIF', 'ISK', 'KYD', 'HKD', 'BYN', 'YER', 'PLN', 'GBP',
        'XCD', 'MKD', 'AZN', 'XPF', 'RUB', 'XAF', 'TRY', 'BAM', 'AUD', 'SOS',
        'INR', 'IQD', 'MXN', 'RWF', 'KES', 'AFN', 'LBP', 'LVL', 'MAD', 'SDG',
        'DZD', 'CHF', 'ZAR', 'TWD', 'DKK', 'LRD', 'AMD', 'KHR', 'VUV', 'DOP',
        'IDR', 'DJF', 'VND', 'MOP', 'KGS', 'XDR', 'LAK', 'ERN', 'MDL', 'MYR',
        'NIO', 'VEF', 'BHD', 'PKR', 'SAR', 'ILS', 'ETB', 'GYD', 'CRC', 'MVR',
        'SZL', 'SBD', 'LSL', 'BZD', 'GIP', 'SYP', 'MNT', 'EGP', 'MRO', 'EUR',
        'CVE', 'BRL', 'GNF', 'KPW', 'NAD', 'HTG', 'UZS', 'MMK', 'KMF', 'GEL',
        'MZN', 'GMD', 'HUF', 'LYD', 'OMR', 'NZD', 'FJD', 'RON', 'SGD', 'BBD',
        'AWG', 'BGN', 'GTQ', 'MUR', 'NOK', 'JPY', 'JOD', 'MWK', 'JMD', 'TOP',
        'CZK', 'CAD', 'ALL', 'ARS', 'COP', 'CUP', 'RSD', 'XOF', 'SCR', 'CNY',
        'USD', 'HNL', 'TTD', 'THB', 'NGN', 'UAH', 'TMT', 'AOA', 'IRR', 'BOB',
        'SEK', 'PGK', 'PEN', 'SRD', 'BSD', 'KWD', 'UGX', 'PAB', 'UYU', 'ZMW',
        'WST', 'PHP', 'FKP', 'AED', 'BTC', 'STD']

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days, free_currencyconverter_api=False):
        if not free_currencyconverter_api:
            raise UserError(
                _("Free Currencyconverter API, was not configured. "
                  "Go to https://free.currencyconverterapi.com/free-api-key "
                  "to get new one, and configure it on server parameters."))

        url = ('https://free.currencyconverterapi.com/api/v6/convert?q=%s'
               '&compact=ultra&apiKey=%s')

        for curr in currency_array:
            rate_key = '%s_%s' % (main_currency, curr)
            rawfile = self.get_url(
                url % (rate_key, free_currencyconverter_api))
            rate = literal_eval(rawfile.decode("utf8"))[rate_key]

            self.updated_currency[curr] = rate
            _logger.debug(
                "Rate retrieved : 1 %s = %s %s" % (main_currency, rate, curr)
            )
        return self.updated_currency, self.log_info
