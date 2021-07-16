# Copyright 2021 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_res_currency_move_state(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_currency_move
        SET state = 'cancel'
        WHERE state = 'cancelled'
        """,
    )


def update_res_currency_move_line_state(cr):
    openupgrade.logged_query(
        cr,
        """
        UPDATE res_currency_move_line
        SET state = 'cancel'
        WHERE state = 'cancelled'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    update_res_currency_move_state(env.cr)
    update_res_currency_move_line_state(env.cr)
