##############################################################################
#
#    Currency rate date check module for OpenERP
#    Copyright (C) 2012-2013 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        ctx = self._context
        if ctx.get('date') and not ctx.get('disable_rate_date_check'):
            date = ctx.get('date')
            for currency in self:
                if ctx.get('company_id'):
                    comp_obj = self.env['res.company']
                    company = comp_obj.browse(ctx.get('company_id'))
                else:
                    company = self.env['res.users']._get_company()
                # If it's the company currency, don't do anything
                # (there's just one old rate at 1.0)
                if company.currency_id.id == currency.id:
                    continue
                else:
                    # Now we do the real work !
                    self._cr.execute("""
                        SELECT rate, name FROM res_currency_rate
                        WHERE currency_id = %s
                        AND name <= %s
                        ORDER BY name desc LIMIT 1
                    """, (currency.id, date))
                    if self._cr.rowcount:
                        rate_date = self._cr.fetchone()[1]
                        rate_date_dt = fields.Datetime.from_string(rate_date)
                        date_dt = fields.Datetime.from_string(date)
                        max_delta = company.currency_rate_max_delta

                        if (date_dt - rate_date_dt).days > max_delta:
                            raise Warning(
                                _("You are requesting a rate conversion on {} "
                                  "for currency {} but the nearest "
                                  "rate before that date is dated {} and the "
                                  "maximum currency rate time delta for your "
                                  "company is {} days").format(date,
                                                               currency.name,
                                                               rate_date,
                                                               max_delta)
                            )
                    else:
                        raise Warning(
                            _("You are requesting a rate conversion on {} "
                              "for currency {} but no rates have been defined "
                              "yet").format(date, currency.name)
                        )
        return super(ResCurrency, self)._compute_current_rate()
