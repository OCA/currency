This module adds `Wise.com <https://wise.com/>`_ as a currency exchange rates
provider for ``currency_rate_update``.

It is meant as a *worldwide* complement to the built-in ECB provider: the ECB
provider gives the official European, EUR-centric daily reference, while Wise
provides a global rate source with the following advantages:

* **Rate quality**: Wise returns the interbank mid-market rate. On a working day,
  aligned with the ECB fixing, it tracks the ECB reference very closely (closer
  than xe.com in our measurements) and applies no markup to the published rate.
* **Worldwide coverage**: Wise quotes around 164 currencies, against the 29 of
  the ECB reference list, including currencies the ECB does not publish (e.g.
  AED, COP). ECB stays the European reference; Wise extends accurate rates to
  the rest of the world.
* **Stable API**: rates are fetched through an authenticated JSON API rather than
  by scraping a web page, which keeps updates robust over time.
* **Efficient and historical**: only the configured currency pairs are requested
  (not a whole table), and past rates can be retrieved by timestamp or date
  range (daily/hourly/minute granularity), which is useful for backfill and
  corrections.

A Wise.com API token is required (see Configuration).
