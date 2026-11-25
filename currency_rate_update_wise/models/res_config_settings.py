# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2026 Altixia (https://altixia.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    wise_api_key = fields.Char(
        string="API Key",
        related="company_id.wise_api_key",
        readonly=False,
        groups="base.group_system",
    )
