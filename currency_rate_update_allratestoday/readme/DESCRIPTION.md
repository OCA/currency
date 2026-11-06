This module adds [AllRatesToday](https://allratestoday.com/) as a
currency rates provider. Instead of a market feed, it loads the table that
one named publisher printed for the day: a central bank or tax authority
such as the ECB, the Reserve Bank of India, HMRC, the Central Bank of
Kenya or the Bank of Canada. Over 120 publishers are covered, each by its
short code (`ecb`, `rbi`, `hmrc`, `cbk`, ...).

That is the rate many tax, customs and statutory accounting rules require
("the rate published by the central bank on the invoice date"), which the
other providers cannot supply for most countries.

Publishers quote in different directions (the ECB prints foreign currency
per 1 EUR, the RBI prints INR per 1 foreign unit). The module normalises
every table to the publisher's home currency and rebases it to the
company currency, so the direction stored in Odoo is always the one
`currency_rate_update` expects.

The latest table is fetched keylessly. Past dates (the update wizard with
a date range) need an AllRatesToday API key on a paid plan.
