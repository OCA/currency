This module provides base for building exchange rates providers and bundles
following built-in providers:

 * **European Central Bank** (ported by Grzegorz Grzelak - OpenGLOBE.pl):
   reference rates are based on the regular daily query procedure between
   central banks within and outside the European System of Central Banks,
   which normally takes place at 2:15 p.m. (14:15) ECB time. Source is in
   EUR, for more details see `corresponding ECB page <https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html>`_.

This module is compatible with ``currency_rate_inverted`` module provided by
OCA, that allows to maintain exchange rates in inverted format, helping to
resolve rounding issues.
