=========
Cash Flow
=========

Overview
========

``cash_flow`` is a custom Odoo module for managing cashboxes and cash flow:

- cashboxes with assigned cashiers and cities
- cash flow transactions (actual and planned)
- DDS categories and articles
- cashbox transfers
- forecast wizard (payment calendar)
- printable reports


Main Models
===========

- ``cash.flow.cashbox``
- ``cash.flow.transaction``
- ``cash.flow.dds.category``
- ``cash.flow.dds.article``
- ``cash.flow.transfer``


Wizards
=======

- ``cash.flow.forecast.wizard``


Reports
=======

- ``Cashbox Balances``
- ``DDS Article Turnover``


Key Business Rules
==================

- Planned transactions must have a future date.
- Transfer posting creates income/expense transactions.
- Cashiers are restricted to their own cashboxes by security rules.


Master Data and Translations
============================

- Demo data is provided in ``demo/cash_flow_demo.xml``.
- Translations are stored in ``i18n/*.po``.


Installation
============

1. Add the module path to your Odoo ``addons_path``.
2. Update app list.
3. Install module ``Cash Flow``.

CLI example:

.. code-block:: bash

   odoo -d <db_name> -i cash_flow --addons-path=<paths>


Run Tests
=========

Use Odoo test mode:

.. code-block:: bash

   odoo -d <db_name> -u cash_flow --test-enable --stop-after-init --workers=0

Test files:

- ``tests/test_cash_flow_cashbox.py``
- ``tests/test_cash_flow_transaction.py``
- ``tests/test_cash_flow_dds_article.py``
- ``tests/test_cash_flow_dds_category.py``
- ``tests/test_cash_flow_transfer.py``
