# Copyright 2021 VanMoof (<https://vanmoof.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models

# put this object into the context key '__bypass_update_checks' to disable
# the AccountMove _check_lock_date and the AccountMoveLine _update_check
bypass_update_checks = object()


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def _check_lock_date(self):
        """Do not raise when the entry is prior to the lock date if 'bypass_update_checks'
        is True in the context."""
        if self._context.get('__bypass_update_checks', False) == bypass_update_checks:
            return True
        return super()._check_lock_date()
