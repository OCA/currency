To use this module, you need to add the security group 'Monthly currency rates'
to your user, so that a 'Monthly rates' smart button appears on the currency
form view.

In order to compute any amount in another currency using monthly rates, you
only have to pass `monthly_rate=True` in the context of `res.currency.compute`
method :

.. code:: python

    to_amount = from_currency.with_context(monthly_rate=True).compute(from_amount, to_currency)

Issues
======

* Monthly currency rates have to be created manually as no automatic updates
  is implemented yet.
