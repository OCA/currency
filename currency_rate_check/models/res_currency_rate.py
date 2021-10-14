# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools import misc


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    @api.multi
    def name_get(self):
        """Override to show the rate and date"""
        res = []
        if self.env.context.get('rate_check_name_get', False):
            for record in self:
                rate_date = misc.format_date(self.env, record.name)
                res.append(
                    (record.id, '{rate} ({rate_date})'.format(
                        rate=record.rate, rate_date=rate_date
                    ))
                )
            return res
        return super(ResCurrencyRate, self).name_get()
