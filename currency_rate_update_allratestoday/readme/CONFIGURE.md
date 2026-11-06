1.  Go to *Invoicing \> Configuration \> Currency Rates Providers*.
2.  Create a provider and choose *AllRatesToday (official central-bank
    rates)* as the *Source Service*.
3.  Set the *Publisher code*: the short code of the central bank or tax
    authority whose table your company must use. The list is at
    <https://allratestoday.com/central-bank-rates-api/institutions/>
    (default `ecb`).
4.  Optionally paste an *API key* (free at
    <https://allratestoday.com/register>). It is only needed to load past
    dates, which require a paid plan.
5.  Optionally pin a *Rate type* (`buy`, `sell`, `middle`, `reference`,
    ...) when the publisher prints several series for the same pair.
6.  Pick the currencies to update. The list offered is the set of
    currencies in the publisher's latest table.
