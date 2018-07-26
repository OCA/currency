# Copyright 2012-2018 Akretion, FIEF Management S.A.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    'name': "Currency Rate Date Check",
    'summary': "Make sure currency rates used are always up-to-date",
    'version': '11.0.1.0.0',
    'category': 'Financial Management/Configuration',
    'website': "https://github.com/OCA/currency",
    'author': "Akretion,"
              "Odoo Community Association (OCA),"
              "FIEF Management S.A.",
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        "base"
    ],
    'data': [
        "views/company_view.xml"
    ],
    'images': [
        'images/date_check_error_popup.jpg',
        'images/date_check_company_config.jpg',
        ],
}
