# Copyright 2018 Eficent (https://www.eficent.com)
# @author: Jordi Ballester <jordi.ballester@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    numeric_code = fields.Char(
        string='Numeric Code',
        help="ISO Numeric Code for currency, according to ISO 4217 standard.")
    full_name = fields.Char(string='Full name',
                            help="Currency name, according to ISO 4217 "
                                 "standard",
                            translate=True)
