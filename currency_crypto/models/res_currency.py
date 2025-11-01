from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    name = fields.Char(size=4)
