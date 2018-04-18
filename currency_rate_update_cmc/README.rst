.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================================
Currency Rate Update Coin Market Cap
====================================

This module introduces the ability to download the exchange rates associated to
crypto currencies from https://coinmarketcap.com


Installation
============

This module depends on *currency_rate_update*, found
in https://github.com/OCA/currency.

It is advisable to install the module *currency_rate_inverted*, found in
https://github.com/OCA/currency, to store the exchange rate in inverted
format and avoid rounding issues for crypto currencies that are very large
compared to the main company currency.


Configuration
=============

To convert amounts from one currency to another using the inverse method,
you have to go to 'Accounting / Configuration / Miscellaneous / Currencies'.
Then select the foreign currency that you wish to maintain inversion for
and set the flag 'Inverted exchange rate'.

#. Go to *Invoicing / Configuration / Accounting / Currencies* and create the
   required crypto currencies. See https://coinmarketcap.com/coins/views/all
   for supported currencies.
#. Go to *Invoicing / Configuration / Accounting / Currency Rate Update* and
   create a new Update Service indicating Webservice to use = 'Coin Market Cap'.


Usage
=====

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

Images
------

 * Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Jordi Ballester Alomar - Eficent (www.eficent.com)
* Ross Golder


Do not contact contributors directly about support or help with technical issues.

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
