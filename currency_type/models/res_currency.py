# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    currency_type = fields.Selection(
        selection=[
            ("none", "None"),
            ("sell", "Sell"),
            ("buy", "Buy"),
        ],
        default="none",
        required=True,
        index=True,
    )
