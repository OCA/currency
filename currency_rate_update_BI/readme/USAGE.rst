After configuration, currency rates are automatically updated based on
your schedule. To manually update rates:

#. Go to *Invoicing > Configuration > Currency Rates Providers*
#. Select the Bank Indonesia provider
#. Click *Action > Update Rates Wizard*
#. Set the date range (From/To dates)
#. Click *Update* to fetch rates from Bank Indonesia

To view the fetched rates:

#. Go to *Invoicing > Configuration > Currencies*
#. Select a currency (e.g., USD)
#. Open the *Rates* tab to see historical exchange rates

The rates are fetched from Bank Indonesia's official webservice at
https://www.bi.go.id/biwebservice/wskursbi.asmx and represent the
middle rate (average of buy/sell rates) for each currency pair.
