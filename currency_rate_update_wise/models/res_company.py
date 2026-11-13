# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2026 Altixia (https://altixia.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    wise_api_key = fields.Char(
        string="Wise.com API Key",
        groups="base.group_system",
    )
