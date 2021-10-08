To convert amounts from one currency to another using the inverse method,
you have to go to 'Accounting / Configuration / Miscellaneous / Currencies'.
Then select the foreign currency that you wish to maintain inversion for
and set the flag 'Inverted exchange rate'.

#. Go to *Invoicing / Configuration / Accounting / Currencies* and create the
   required crypto currencies. See https://coinmarketcap.com/coins/views/all
   for supported currencies.
#. Go to *Invoicing / Configuration / Accounting / Currency Rate Update* and
   create a new Update Service indicating Webservice to use 'Coin Market Cap'
   with the Basic Plan or the Standard Plan.

There are two options of Coin Market Cap based on the plan of your account
https://coinmarketcap.com/api/pricing/:

* Basic Plan (including Basic, Startup and Hobbyist): the user does not have access
  to all the endpoints, for example, cannot fetch historical currency rates. The
  update of the currency dates will only fetch the last available price.
* Standard Plan (including Standard, Professional, Enterprise): the user has access
  to most of the API endpoints. The user can select the date ranges to get historical
  rates.
