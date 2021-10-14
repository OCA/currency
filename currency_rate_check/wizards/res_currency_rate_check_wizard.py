# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResCurrencyRateCheckWizard(models.TransientModel):
    _name = 'res.currency.rate.check.wizard'
    _description = 'Currency Rate Check Wizard'

    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
    )
    provider_ids = fields.Many2many(
        string='Providers',
        comodel_name='res.currency.rate.provider',
        column1='wizard_id',
        column2='provider_id',
    )
    currency_ids = fields.Many2many(
        string='Currencies',
        comodel_name='res.currency',
        column1='wizard_id',
        column2='currency_id',
    )
    line_limit = fields.Integer(
        string='Item Limit',
        help="Only journal entries with at most this number of journal items will be "
        "checked",
        default=2
    )
    ref = fields.Char(string='Journal Entry Reference')

    @api.multi
    def action_check(self):
        self.ensure_one()
        missing_rates = []
        for currency_id in self.currency_ids + self.env.user.company_id.currency_id:
            self.env.cr.execute(
                """
                SELECT dates.i::date AS missing, rc.name
                FROM generate_series(
                    %(date_from)s, %(date_to)s, '1 day'::interval
                ) dates(i)
                LEFT JOIN res_currency AS rc ON id = %(currency_id)s
                LEFT JOIN res_currency_rate AS rcr
                ON rcr.name = dates.i
                AND rcr.company_id = %(company_id)s
                AND rcr.currency_id = %(currency_id)s
                WHERE rcr IS NULL
                ORDER BY dates.i ASC;
                """, {
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'company_id': self.env.user.company_id.id,
                    'currency_id': currency_id.id,
                }
            )
            res = self.env.cr.fetchall()
            missing_rates.extend(res)

        if missing_rates:
            message_data = '\n'.join(
                [str((r[0].strftime('%Y-%m-%d'), r[1])) for r in missing_rates]
            )
            raise UserError(_(
                "The following currency rates are missing:\n{}".format(message_data)
                .replace('(', '').replace(')', '').replace('\'', '')
            ))
        res = self.env['account.move.line.currency.check'].action_update_check_lines(
            self.date_from, self.date_to, self.line_limit, self.ref
        )
        if not res:
            raise UserError(_("No incorrect currencies found!"))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Items with invalid rates"),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line.currency.check',
            'target': 'current',
        }
