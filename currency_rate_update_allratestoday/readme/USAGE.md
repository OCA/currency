The scheduled action of `currency_rate_update` loads the latest table
automatically. Use *Update Rates Now* on the provider to load it on
demand, or give the wizard a date range to load the tables of past days
(one request per day; a day without a publication takes the newest table
printed before it, as the publisher's own rules require).

The company currency must appear in the publisher's table, otherwise the
update is refused with a message naming the publisher and the date.
