# Copyright 2009-2016 Camptocamp
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_rates_autoupdate = fields.Boolean(
        string='Automatic Currency Rates (OCA)',
        default=True,
        help='Enable regular automatic currency rates updates',
        oldname='auto_currency_up',
    )
