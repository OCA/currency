# Copyright 2022 Garazd Creation (https://garazd.biz)
# @author: Yurii Razumovskyi (garazdcreation@gmail.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Currency Rate Update NBU",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Allows to download currency exchange rates from "
    "National Bank of Ukraine",
    "author": "Garazd Creation," "Odoo Community Association (OCA),",
    "website": "https://github.com/OCA/currency",
    "license": "AGPL-3",
    "depends": [
        "currency_rate_update",
    ],
    "data": [
        "data/res_currency_rate_provider_data.xml",
    ],
    "installable": True,
}
