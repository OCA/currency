# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    xe_com_account_id = fields.Char(
        string='XE.com Account ID',
    )
    xe_com_account_api_key = fields.Char(
        string='XE.com Account API Key',
    )
