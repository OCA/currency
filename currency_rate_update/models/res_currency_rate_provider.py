# Copyright 2009-2016 Camptocamp
# Copyright 2010 Akretion
# Copyright 2019-2020 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCurrencyRateProvider(models.Model):
    _name = "res.currency.rate.provider"
    _description = "Currency Rates Provider"
    _inherit = ["mail.thread"]
    _order = "name"

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_name = fields.Char(
        string="Currency Name", related="company_id.currency_id.name"
    )
    active = fields.Boolean(default=True)
    service = fields.Selection(
        string="Source Service",
        selection=[("none", "None")],
        default="none",
        required=True,
    )
    available_currency_ids = fields.Many2many(
        string="Available Currencies",
        comodel_name="res.currency",
        compute="_compute_available_currency_ids",
    )
    currency_ids = fields.Many2many(
        string="Currencies",
        comodel_name="res.currency",
        column1="provider_id",
        column2="currency_id",
        required=True,
        help="Currencies to be updated by this provider",
    )
    name = fields.Char(string="Name", compute="_compute_name", store=True)
    interval_type = fields.Selection(
        string="Units of scheduled update interval",
        selection=[("days", "Day(s)"), ("weeks", "Week(s)"), ("months", "Month(s)")],
        default="days",
        required=True,
    )
    interval_number = fields.Integer(
        string="Scheduled update interval", default=1, required=True
    )
    update_schedule = fields.Char(
        string="Update Schedule", compute="_compute_update_schedule"
    )
    last_successful_run = fields.Date(string="Last successful update")
    next_run = fields.Date(
        string="Next scheduled update", default=fields.Date.today, required=True
    )

    _sql_constraints = [
        (
            "service_company_id_uniq",
            "UNIQUE(service, company_id)",
            "Service can only be used in one provider per company!",
        ),
        (
            "valid_interval_number",
            "CHECK(interval_number > 0)",
            "Scheduled update interval must be greater than zero!",
        ),
    ]

    @api.depends("service")
    def _compute_name(self):
        for provider in self:
            provider.name = list(
                filter(
                    lambda x: x[0] == provider.service,
                    self._fields["service"].selection,
                )
            )[0][1]

    @api.depends("active", "interval_type", "interval_number")
    def _compute_update_schedule(self):
        for provider in self:
            if not provider.active:
                provider.update_schedule = _("Inactive")
                continue

            provider.update_schedule = _("%(number)s %(type)s") % {
                "number": provider.interval_number,
                "type": list(
                    filter(
                        lambda x: x[0] == provider.interval_type,
                        self._fields["interval_type"].selection,
                    )
                )[0][1],
            }

    @api.depends("service")
    def _compute_available_currency_ids(self):
        Currency = self.env["res.currency"]

        for provider in self:
            provider.available_currency_ids = Currency.search(
                [("name", "in", provider._get_supported_currencies())]
            )

    def _update(self, date_from, date_to, newest_only=False):
        Currency = self.env["res.currency"]
        CurrencyRate = self.env["res.currency.rate"]
        is_scheduled = self.env.context.get("scheduled")
        for provider in self:
            try:
                data = provider._obtain_rates(
                    provider.company_id.currency_id.name,
                    provider.currency_ids.mapped("name"),
                    date_from,
                    date_to,
                )
                if data:
                    data = data.items()
            except BaseException as e:
                _logger.warning(
                    'Currency Rate Provider "%s" failed to obtain data since'
                    " %s until %s"
                    % (
                        provider.name,
                        date_from,
                        date_to,
                    ),
                    exc_info=True,
                )
                provider.message_post(
                    subject=_("Currency Rate Provider Failure"),
                    body=_(
                        'Currency Rate Provider "%s" failed to obtain data'
                        " since %s until %s:\n%s"
                    )
                    % (
                        provider.name,
                        date_from,
                        date_to,
                        str(e) if e else _("N/A"),
                    ),
                )
                continue

            if not data:
                # Try again if there is no data yet
                continue
            if newest_only:
                data = [max(data, key=lambda x: fields.Date.from_string(x[0]))]

            for content_date, rates in data:
                timestamp = fields.Date.from_string(content_date)
                for currency_name, rate in rates.items():
                    if currency_name == provider.company_id.currency_id.name:
                        continue

                    currency = Currency.search([("name", "=", currency_name)], limit=1)
                    if not currency:
                        raise UserError(
                            _("Unknown currency from %(provider)s: %(rate)s")
                            % {"provider": provider.name, "rate": rate}
                        )
                    rate = provider._process_rate(currency, rate)

                    record = CurrencyRate.search(
                        [
                            ("company_id", "=", provider.company_id.id),
                            ("currency_id", "=", currency.id),
                            ("name", "=", timestamp),
                        ],
                        limit=1,
                    )
                    if record:
                        record.write({"rate": rate, "provider_id": provider.id})
                    else:
                        record = CurrencyRate.create(
                            {
                                "company_id": provider.company_id.id,
                                "currency_id": currency.id,
                                "name": timestamp,
                                "rate": rate,
                                "provider_id": provider.id,
                            }
                        )

            if is_scheduled:
                provider._schedule_last_successful_run()
                provider._schedule_next_run()

    def _schedule_last_successful_run(self):
        self.last_successful_run = self.next_run

    def _schedule_next_run(self):
        self.ensure_one()
        self.next_run = (
            datetime.combine(self.next_run, time.min) + self._get_next_run_period()
        ).date()

    def _process_rate(self, currency, rate):
        self.ensure_one()

        Module = self.env["ir.module.module"]

        currency_rate_inverted = Module.sudo().search(
            [("name", "=", "currency_rate_inverted"), ("state", "=", "installed")],
            limit=1,
        )

        if type(rate) is dict:
            inverted = rate.get("inverted", None)
            direct = rate.get("direct", None)
            if inverted is None and direct is None:
                raise UserError(
                    _("Invalid rate from %(provider)s for %(currency)s : %(rate)s")
                    % {"provider": self.name, "currency": currency.name, "rate": rate}
                )
            elif inverted is None:
                inverted = 1 / direct
            elif direct is None:
                direct = 1 / inverted
        else:
            rate = float(rate)
            direct = rate
            inverted = 1 / rate

        value = direct
        if (
            currency_rate_inverted
            and currency.with_company(self.company_id).rate_inverted
        ):
            value = inverted

        return value

    def _get_next_run_period(self):
        self.ensure_one()

        if self.interval_type == "days":
            return relativedelta(days=self.interval_number)
        elif self.interval_type == "weeks":
            return relativedelta(weeks=self.interval_number)
        elif self.interval_type == "months":
            return relativedelta(months=self.interval_number)

    @api.model
    def _scheduled_update(self):
        _logger.info("Scheduled currency rates update...")

        today = fields.Date.context_today(self)
        providers = self.search(
            [
                ("company_id.currency_rates_autoupdate", "=", True),
                ("active", "=", True),
                ("next_run", "<=", today),
            ]
        )
        if providers:
            _logger.info(
                "Scheduled currency rates update of: %s"
                % ", ".join(providers.mapped("name"))
            )
            for provider in providers.with_context({"scheduled": True}):
                date_from = (
                    (provider.last_successful_run + relativedelta(days=1))
                    if provider.last_successful_run
                    else (provider.next_run - provider._get_next_run_period())
                )
                date_to = provider.next_run
                current_utc_hour = datetime.now().hour
                _logger.debug(
                    "Provider %s date_to=%s today=%s, current hour %s UTC",
                    provider.name,
                    date_to,
                    today,
                    current_utc_hour,
                )
                provider._update(date_from, date_to, newest_only=True)
                _logger.info("Currency rates updated from %s", provider.name)

        _logger.info("Scheduled currency rates update complete.")

    def _get_supported_currencies(self):
        # pragma: no cover
        self.ensure_one()
        return []

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        # pragma: no cover
        self.ensure_one()
        return {}
