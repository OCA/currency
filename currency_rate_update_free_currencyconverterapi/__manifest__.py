# Copyright 2018 PESOL
# Copyright 2018 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Currency Rate Update https://free.currencyconverterapi.com/',
    'version': '11.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': 'Allows to download crypto currency exchange rates from '
               'https://free.currencyconverterapi.com/',
    'author': 'PESOL,'
              'Odoo Community Association (OCA),',
    'website': 'https://github.com/OCA/currency',
    'license': 'AGPL-3',
    'depends': [
        'currency_rate_update',
    ],
    'data': [
        'data/free_currencyconverter_api.xml'
    ],
    'installable': True
}
