.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
Account Cryptocurrency
======================

This module provides basic support for the management of cryptocurrencies.

#. Cryptocurrencies are commonly considered property from a
   taxation standpoint.

#. This means that every time that you receive or send cryptocurrencies, you
   are entering into a taxable transaction, and will need to report on the
   gain/loss resulting from the receipt/issue of the cryptocurrency.

#. When you receive cryptocurrencies (in exchange for goods delivered,
   service rendered or because you mined it), that translates into taxable
   income to the recipient. The valuation should be based on the market value of
   the cryptocurrency at the time of receipt, and it can be provided by a
   third party (e.g. the exchange platform) or needs to be identified by
   you somehow.

#. You have to retain the cost of the crytptocurrency for as long as you keep
   it.

#. When you pay out cryptocurrencies (in exchange for goods or services
   purchased, or if you exchanged fpr another crypto or normal currency) this
   constitutes again a taxable transaction. In that case the gain/loss is
   computed as the difference between the cost of the cryptocurrency that
   you pay with, and the value of what you receive back, valued in your
   operating normal currency.


Installation
============

* Install the module 'account_invoicing' to be able to display the menus.

Configuration
=============

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


Usage
=====

* If you have negotiated your invoices with customers / suppliers using
  crypto currencies, you can indicate them in the corresponding invoice.

* When you receive/send payments you can indicate the cryptocurrency that
  you want to use for the payment. Once the payment has been posted you will
  be able to navigate to the associated currency moves.

* You cannot make internal transfers using cryptocurrencies.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/259/11.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/currency/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Jordi Ballester <jordi.ballester@eficent.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
