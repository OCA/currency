To configure the module, go to *Invoicing > Configuration > Multi-currencies > Rate Auto-download* and create one or several services to download rates from the Internet.

Then, go to the page *Invoicing > Configuration > Settings* and, in the section *Multi Currencies*, make sure that the option *Automatic Currency Rates Download* is enabled.

In developper mode, in the menu *Settings > Technical > Scheduled Actions*, make sure that the action *Currency Rate Update* is active. If you want to run it immediately, use the button *Run Manually*.

This module is compatible with OCA module 'currency_rate_inverted' also found in OCA/currency repository, that allows to maintain exchange rates in inverted format, helping to resolve rounding issues.
