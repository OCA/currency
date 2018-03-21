# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, models, _


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.constrains('journal_id')
    def _check_journal_id_crypto(self):
        if self.filtered('journal_id.currency_id.inventoried'):
            raise exceptions.Warning(
                _('You cannot encode bank statements associated to '
                  'crypto currencies.'))
