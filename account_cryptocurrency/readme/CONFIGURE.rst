#. For the user that will do the configuration, make sure to activate the
   option 'Show Full Accounting Features' in the user profile.

#. Activate the Multi-Currency in 'Invoicing / Configuration /
   Settings / Multi-Currencies.

#. Create the cryptocurrency in 'Invoicing / Configuration / Accounting /
   Currencies'. Complete the following fields:  'Inventoried', 'Valuation
   Method'. Indicate the desired rounding factor.

#. Add to the cryptocurrency an 'Inventory Account'. This Account must
   indicate in field 'Account Currency' the same currency.

#. Create an Account Journal associated to the payments of the crypto
   currency, in 'Invoicing / Configuration / Accounting / Journals'. Indicate
   in the 'Currency' field the cryptocurrency. In the 'Default Credit Account'
   and 'Default Debit Account' you should indicate a new Account of type
   'Expenses', with a name similar to 'Cryptocurrency X Gain/Loss'. The new
   Account must also refer to the cryptocurrency account.


Additional remarks:

 * In case that your company currency is not EUR, make sure that the main
   company currency has no exchange rates. Go to 'Invoicing / Configuration /
   Accounting / Currencies' and for the company currency press the
   button 'Rates' and delete any rate listed.

 * The maximum allowed decimal places associated to currencies has been
   increased to 18, that is what Ethereum cryptocurrency accepts as the
   maximum divisibility.
