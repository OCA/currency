.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

========================
Currency Rate Date Check
========================

This module adds a check on dates when doing currency conversion in Odoo.
It checks that the currency rate used to make the conversion
is not more than N days away from the date of the amount to convert.
If no rates have been defined for the currency, a warning is displayed too.

Configuration
=============

The maximum number of days of the interval can be configured on the company form.

Usage
=====

This module is automatically used whenever an amount computation involves a currency that differs from the user's company currency.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/currency/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>
* Maxence Groine <mgroine@fiefmanage.ch>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
