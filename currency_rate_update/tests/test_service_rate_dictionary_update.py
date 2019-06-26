# © 2019 Duc, Dao Dong
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ..services.currency_getter_interface import CurrencyGetterInterface


class TestServiceRateDirectUpdate(CurrencyGetterInterface):

    code = 'TSRDU'
    name = 'Test Service Rate Direct Update'
    supported_currency_array = ["EUR", "USD"]

    def rate_retrieve(self):
        res = {}
        res['rate_currency'] = 1.13
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        if main_currency != 'EUR':
            main_curr_data = self.rate_retrieve()
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'EUR':
                rate = 1 / main_curr_data['rate_currency']
            else:
                curr_data = self.rate_retrieve()
                if main_currency == 'EUR':
                    rate = curr_data['rate_currency']
                else:
                    rate = (curr_data['rate_currency'] /
                            main_curr_data['rate_currency'])
            self.updated_currency[curr] = {
                'direct': rate
            }
        return self.updated_currency, self.log_info


class TestServiceRateInvertedUpdate(CurrencyGetterInterface):

    code = 'TSRIU'
    name = 'Test Service Rate Inverted Update'
    supported_currency_array = ["EUR", "USD"]

    def rate_retrieve(self):
        res = {}
        res['rate_currency'] = 1.13
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        if main_currency != 'EUR':
            main_curr_data = self.rate_retrieve()
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'EUR':
                rate = 1 / main_curr_data['rate_currency']
            else:
                curr_data = self.rate_retrieve()
                if main_currency == 'EUR':
                    rate = curr_data['rate_currency']
                else:
                    rate = (curr_data['rate_currency'] /
                            main_curr_data['rate_currency'])
            self.updated_currency[curr] = {
                'inverted': 1/rate
            }
        return self.updated_currency, self.log_info


class TestServiceWrongRateUpdate(CurrencyGetterInterface):

    code = 'TSWRU'
    name = 'Test Service Wrong Rate Update'
    supported_currency_array = ["EUR", "USD"]

    def rate_retrieve(self):
        res = {}
        res['rate_currency'] = 1.13
        return res

    def get_updated_currency(self, currency_array, main_currency,
                             max_delta_days):
        if main_currency in currency_array:
            currency_array.remove(main_currency)
        if main_currency != 'EUR':
            main_curr_data = self.rate_retrieve()
        for curr in currency_array:
            self.validate_cur(curr)
            if curr == 'EUR':
                rate = 1 / main_curr_data['rate_currency']
            else:
                curr_data = self.rate_retrieve()
                if main_currency == 'EUR':
                    rate = curr_data['rate_currency']
                else:
                    rate = (curr_data['rate_currency'] /
                            main_curr_data['rate_currency'])
            self.updated_currency[curr] = {
                'rate': rate
            }
        return self.updated_currency, self.log_info
