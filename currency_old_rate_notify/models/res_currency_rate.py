# Copyright 2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from collections import defaultdict
from datetime import timedelta

from odoo import _, api, fields, models

logger = logging.getLogger(__name__)

MAX_DAYS_DEFAULT = 3


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    @api.model
    def _prepare_notify_rates_too_old(
        self, user, cur2companies, company2name, max_days
    ):
        res = False
        msg = []
        user_company_ids = user.company_ids.ids
        for cur_code, company_ids in cur2companies.items():
            intersection_company_ids = list(set(company_ids) & set(user_company_ids))
            if intersection_company_ids:
                # Write company name in message only when there are several companies
                if len(user_company_ids) == 1:
                    msg.append("<li>%s</li>" % cur_code)
                else:
                    msg.append(
                        "<li>%s (%s)</li>"
                        % (
                            cur_code,
                            ", ".join(
                                [
                                    company2name[c_id]
                                    for c_id in intersection_company_ids
                                ]
                            ),
                        )
                    )
        if msg:
            # force title msg to user's lang
            self = self.with_context(lang=user.lang)
            res = {
                "title": _("Currency rates older than %d days", max_days),
                "sticky": True,
                "message": "<ul>%s</ul>" % "".join(msg),
                # TODO remove once bug is fixed in the PR to mig web_notify in v16
                # https://github.com/OCA/web/pull/2412
                # We also need the fix for HTML in "message
                "target": user.partner_id,
            }
        return res

    @api.model
    def _notify_rates_too_old_groups(self):
        return self.env.ref("account.group_account_manager")

    @api.model
    def _notify_rates_get_max_days(self):
        max_days_str = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "currency_old_rate_notify.max_days", default=str(MAX_DAYS_DEFAULT)
            )
        )
        try:
            max_days = int(max_days_str)
            logger.debug("currency_old_rate_warn.max_days = %s", max_days)
        except Exception as e:
            logger.warning(
                "Failed to convert ir.config_parameter "
                "currency_old_rate_warn.max_days value %s to integer. "
                "Error: %s. Using default value %s.",
                max_days_str,
                e,
                MAX_DAYS_DEFAULT,
            )
            max_days = MAX_DAYS_DEFAULT
        return max_days

    @api.model
    def _notify_rates_company_domain(self):
        return []

    @api.model
    def _notify_rates_currency_domain(self):
        return []

    @api.model
    def notify_rates_too_old(self):
        max_days = self._notify_rates_get_max_days()
        today = fields.Date.context_today(self)
        limit_date = today - timedelta(max_days)
        logger.debug("notify_rates_too_old limit_date=%s", limit_date)
        companies = self.env["res.company"].search(self._notify_rates_company_domain())
        currencies = self.env["res.currency"].search(
            self._notify_rates_currency_domain()
        )
        cur2companies = defaultdict(list)
        company2name = {c.id: c.display_name for c in companies}
        for currency in currencies:
            for company in companies:
                if currency == company.currency_id:
                    continue
                last_rate = self.search(
                    [
                        ("company_id", "in", (False, company.id)),
                        ("currency_id", "=", currency.id),
                    ],
                    order="name desc",
                    limit=1,
                )
                if not last_rate or (last_rate and last_rate.name < limit_date):
                    cur2companies[currency.name].append(company.id)
        if cur2companies:
            logger.info(
                "Some currencies have rates older than %d days: %s",
                max_days,
                ", ".join(cur2companies),
            )
            groups = self._notify_rates_too_old_groups()
            users = self.env["res.users"].search([("groups_id", "in", groups.ids)])
            for user in users:
                notify_res = self._prepare_notify_rates_too_old(
                    user, cur2companies, company2name, max_days
                )
                if notify_res:
                    logger.info(
                        "Notifying user %s about currencies with old rates",
                        user.display_name,
                    )
                    user.notify_warning(**notify_res)
                else:
                    logger.info(
                        "User %s is not notified because he is not in one "
                        "of the impacted companies",
                        user.display_name,
                    )
        else:
            logger.info("There are no outdated currency rates")
