# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models

from .account_move import bypass_update_checks


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def _update_check(self):
        """Do not raise when the entry is posted or reconciled if 'bypass_update_checks'
        is True in the context."""
        if self._context.get('__bypass_update_checks', False) == bypass_update_checks:
            return True
        return super()._update_check()
