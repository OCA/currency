# Copyright 2021 ForgeFlow S.L.
# Copyright 2018 Fork Sand Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

import odoo.tests.common as common


class TestAccountCryptocurrency(common.TransactionCase):
    def setUp(self):
        res = super(TestAccountCryptocurrency, self).setUp()
        self.company = self.env.ref("base.main_company")
        self.receivable_account = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_receivable").id,
                ),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        self.payable_account = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_payable").id,
                ),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        self.account_expenses = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_expenses").id,
                ),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )
        self.account_revenue = self.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    self.env.ref("account.data_account_type_revenue").id,
                ),
                ("company_id", "=", self.company.id),
            ],
            limit=1,
        )

        self.inventory_account = self.env["account.account"].create(
            {
                "name": "CC Inventory",
                "code": "9991",
                "company_id": self.company.id,
                "user_type_id": self.env.ref(
                    "account.data_account_type_current_assets"
                ).id,
            }
        )
        self.to_inventory_account = self.env["account.account"].create(
            {
                "name": "CC To Inventory",
                "code": "9992",
                "company_id": self.company.id,
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.company.income_currency_exchange_account_id = self.env[
            "account.account"
        ].create(
            {
                "name": "Exchange Profit",
                "code": "9993",
                "company_id": self.company.id,
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.company.expense_currency_exchange_account_id = self.env[
            "account.account"
        ].create(
            {
                "name": "Exchange Loss",
                "code": "9994",
                "company_id": self.company.id,
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        self.currency_cc = (
            self.env["res.currency"]
            .with_company(self.company)
            .create(
                {
                    "name": "CC",
                    "rounding": 0.010000,
                    "symbol": "CC",
                    "position": "after",
                    "inventoried": True,
                    "valuation_method": "fifo",
                    "inventory_account_id": self.inventory_account.id,
                }
            )
        )
        self.customer = self.env["res.partner"].create(
            {
                "name": "Test customer",
                "property_account_receivable_id": self.receivable_account.id,
            }
        )
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Test supplier",
                "property_account_payable_id": self.payable_account.id,
            }
        )
        self.sale_journal = self.env["account.journal"].create(
            {
                "name": "Customer Invoices (TEST)",
                "code": "INVT",
                "type": "sale",
                "company_id": self.company.id,
                "default_account_id": self.account_revenue.id,
            }
        )
        self.purchase_journal = self.env["account.journal"].create(
            {
                "name": "Vendor Bills (TEST)",
                "code": "BILLT",
                "type": "purchase",
                "company_id": self.company.id,
                "default_account_id": self.account_expenses.id,
            }
        )
        self.cc_journal = self.env["account.journal"].create(
            {
                "name": "CC Payments Journal",
                "code": "CC",
                "type": "bank",
                "company_id": self.company.id,
                "default_account_id": self.to_inventory_account.id,
                "payment_debit_account_id": self.to_inventory_account.id,
                "payment_credit_account_id": self.to_inventory_account.id,
            }
        )
        # We want to make sure that the company has no rates, that would
        # screw up the conversions.
        company_rates = self.env["res.currency.rate"].search(
            [("currency_id", "=", self.company.currency_id.id)]
        )
        company_rates.unlink()

        return res

    def _check_account_balance(self, account):
        balance = sum(
            self.env["account.move.line"]
            .search([("account_id", "=", account.id), ("move_id.state", "=", "posted")])
            .mapped("balance")
        )
        return balance

    def test_01(self):
        """Implements test for scenario 1 as defined in the repository
        readme"""
        ####
        # Day 1: Invoice Cust/001 to customer (expressed in CC)
        # Market value of CC (day 1): 1 CC = $0.5
        # * Dr. 100 CC / $50 - Accounts receivable
        # * Cr. 100 CC / $50 - Revenue
        ####
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-01",
                "rate": 2,
            }
        )
        invoice_cust_001 = self.env["account.move"].create(
            {
                "partner_id": self.customer.id,
                "journal_id": self.sale_journal.id,
                "move_type": "out_invoice",
                "currency_id": self.currency_cc.id,
                "company_id": self.company.id,
                "date": time.strftime("%Y") + "-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.account_revenue.id,
                        },
                    )
                ],
            }
        )
        invoice_cust_001.action_post()
        self.assertEqual(invoice_cust_001.amount_residual_signed, 50.0)
        aml = invoice_cust_001.mapped("line_ids").filtered(
            lambda x: x.account_id == self.account_revenue
        )
        self.assertEqual(aml.credit, 50.0)
        #####
        # Day 2: Receive payment for half invoice Cust/001 (in CC)
        # -------------------------------------------------------
        # Market value of CC (day 2): 1 CC = $0.8

        # Payment transaction:
        # * Dr. 50 CC / $40 - CC To Inventory (valued at market price
        # at the time of receiving the coins)
        # * Cr. 50 CC / $40 - Accounts Receivable

        # Actual receipt of the coins:
        # * Dr. 50 CC / $40 - CC Inventory (valued at market price
        # at the time of receiving the coins)
        # * Cr. 50 CC / $40 - CC To Inventory
        #####
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-02",
                "rate": 1.25,
            }
        )
        # register payment on invoice
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "partner_type": "customer",
                "partner_id": self.customer.id,
                "amount": 50,
                "currency_id": self.currency_cc.id,
                "date": time.strftime("%Y") + "-01-02",
                "journal_id": self.cc_journal.id,
            }
        )
        payment.action_post()
        invoice_line_id = invoice_cust_001.line_ids.filtered(
            lambda x: x.account_id == self.receivable_account
        )
        payment_line_id = payment.move_id.line_ids.filtered(
            lambda x: x.account_id == self.receivable_account
        )
        (invoice_line_id + payment_line_id).reconcile()
        self.assertEqual(invoice_cust_001.state, "posted")
        self.assertEqual(payment_line_id.amount_currency, -50.0)
        self.assertEqual(payment_line_id.credit, 40.0)
        # Inventory of CC (day 2)
        # ----------------------
        # day 2:
        # 50 CC @$0,8/CC (total valuation of coins received /
        # number of coins received)
        cc_ml = payment.res_currency_move_ids.mapped("line_ids")[0]
        self.assertEqual(round(cc_ml.quantity, 2), 50.0)
        self.assertEqual(cc_ml.amount, 40.0)
        self.assertEqual(round(cc_ml.price_unit, 2), 0.8)
        # Balance of the To Inventory account should be 0
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, 0.0)
        # Balance of the Inventory account should be 40
        inventory_balance = self._check_account_balance(self.inventory_account)
        self.assertEqual(inventory_balance, 40.0)
        ####
        # Day 3: Receive remaining payment for invoice Cust/001 (in CC)
        # -------------------------------------------------------------
        # Market value of CC (day 3): 1 CC = $2
        #
        # Payment transaction:
        # * Dr. 50 CC / $100 - CC To Inventory (valued at market price at
        #   the time of receiving the coins)
        # * Cr. 50 CC / $100 - Accounts Receivable
        # Actual receipt of the coins:
        # * Dr. 50 CC / $100 - CC Inventory (valued at market price at the
        # time of receiving the coins)
        # * Cr. 50 CC / $100 - CC To Inventory
        # Full invoice reconciliation. Realization of the full transaction
        # gain/loss:
        # * Dr. 0 CC / $90 - Accounts Receivable
        # * Cr. 0 CC / $90 - Cryptocurrency exchange gain
        ####
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-03",
                "rate": 0.5,
            }
        )
        # register payment on invoice
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "partner_type": "customer",
                "partner_id": self.customer.id,
                "amount": 50,
                "currency_id": self.currency_cc.id,
                "date": time.strftime("%Y") + "-01-03",
                "journal_id": self.cc_journal.id,
            }
        )
        payment.action_post()
        payment_line_id = payment.move_id.line_ids.filtered(
            lambda x: x.account_id == self.receivable_account
        )
        (invoice_line_id + payment_line_id).reconcile()
        self.assertEqual(invoice_cust_001.payment_state, "paid")
        self.assertEqual(payment_line_id.amount_currency, -50.0)
        self.assertEqual(payment_line_id.credit, 100.0)
        # Inventory of CC (day 3)
        # -----------------------
        # day 1:
        # * 50 CC @$0,80/CC
        # day 3:
        # * 50 CC @$2,00/CC
        cc_ml = payment.res_currency_move_ids.mapped("line_ids")[0]
        self.assertEqual(round(cc_ml.quantity, 2), 50.0)
        self.assertEqual(cc_ml.amount, 100.0)
        self.assertEqual(round(cc_ml.price_unit, 2), 2)
        # Balance of the To Inventory account should be 0
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, 0.0)
        # Balance of the Inventory account should be 40
        inventory_balance = self._check_account_balance(self.inventory_account)
        self.assertEqual(inventory_balance, 140.0)
        # Exchange Rate Profit / Loss
        # ---------------------------
        # Profit resulting from exchange rate should be the difference
        # between the money in normal currency that we get after we get paid (
        # 100.00 + 40.00) - what we were supposed to get paid if the exchange
        #  rate had stayed the same (50.00)
        exchange_profit_balance = self._check_account_balance(
            self.company.income_currency_exchange_account_id
        )
        self.assertEqual(exchange_profit_balance, -90.00)
        exchange_expense_balance = self._check_account_balance(
            self.company.expense_currency_exchange_account_id
        )
        self.assertEqual(exchange_expense_balance, 0.0)

        # Day 4: Invoice to supplier Supp/001 (expressed in CC)
        # -----------------------------------------------------
        # Market value of CC (day 4): 1 CC = $4
        # * Cr. 60 CC / $240 - Accounts Payable
        # * Dr. 60 CC / $240 - Expenses
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-04",
                "rate": 0.25,
            }
        )
        invoice_supp_001 = self.env["account.move"].create(
            {
                "partner_id": self.supplier.id,
                "journal_id": self.purchase_journal.id,
                "move_type": "in_invoice",
                "currency_id": self.currency_cc.id,
                "company_id": self.company.id,
                "invoice_date": time.strftime("%Y") + "-01-04",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 60.0,
                            "name": "product that cost 100",
                            "account_id": self.account_expenses.id,
                        },
                    )
                ],
            }
        )
        invoice_supp_001.action_post()
        # Day 5: Pay half invoice of Supp/001 (in CC)
        # -------------------------------------------
        # Market value of CC (day 5): 1 CC = $5
        # Assume FIFO strategy for issuing crypto coins
        # * Dr. 30 CC / $150 - Accounts Payable
        # * Cr. 30 CC / $150 - CC To Inventory
        #
        # * Cr. 30 CC / $24 - CC Inventory (30 CC @$0,80/CC)
        # * Dr. 30 CC / $24 - CC To Inventory
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-05",
                "rate": 0.2,
            }
        )
        # register payment on invoice
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "partner_type": "supplier",
                "partner_id": self.supplier.id,
                "amount": 30,
                "currency_id": self.currency_cc.id,
                "date": time.strftime("%Y") + "-01-05",
                "journal_id": self.cc_journal.id,
            }
        )
        payment.action_post()
        invoice_line_id = invoice_supp_001.line_ids.filtered(
            lambda x: x.account_id == self.payable_account
        )
        payment_line_id = payment.move_id.line_ids.filtered(
            lambda x: x.account_id == self.payable_account
        )
        (invoice_line_id + payment_line_id).reconcile()
        self.assertEqual(invoice_supp_001.state, "posted")
        cc_ml = payment.res_currency_move_ids.mapped("line_ids")[0]
        self.assertEqual(round(cc_ml.quantity, 2), 30.0)
        self.assertEqual(round(cc_ml.amount, 2), 24.0)
        self.assertEqual(round(cc_ml.price_unit, 2), 0.80)
        ####
        # Inventory of CC (day 5)
        # -----------------------
        # day 1:
        # * 20 CC @$0,80/CC
        # day 2:
        # * 50 CC @$2,00/CC
        ####
        # Balance of the Inventory account should be 116
        inventory_balance = self._check_account_balance(self.inventory_account)
        self.assertEqual(inventory_balance, 116.0)
        ####
        # Exchange Rate Profit/Loss
        # -------------------------
        # Profit resulting from exchange rate should be the difference
        # between the cost of the 30 coins at original purchase price
        # ($0,80/CC) and the valuation at the time of paying them ($5,00/CC).
        # That is, a profit of $126,00.
        ####
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, -126.0)
        # Day 6: Pay the other half invoice of Supp/001 (in CC)
        # ----------------------------------------------------
        # Market value of CC (day 6): 1 CC = $5
        # Assume FIFO strategy for issuing crypto coins
        # * Dr. 30 CC / $150 - Accounts Payable
        # * Cr. 30 CC / $150 - CC To Inventory
        #
        # * Cr. 30 CC / $36 - CC Inventory (20 CC @$0,80/CC + 10 CC @$2,00/CC)
        # * Dr. 30 CC / $36 - CC To Inventory
        # register payment on invoice
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
                "partner_type": "supplier",
                "partner_id": self.supplier.id,
                "amount": 30,
                "currency_id": self.currency_cc.id,
                "date": time.strftime("%Y") + "-01-06",
                "journal_id": self.cc_journal.id,
            }
        )
        payment.action_post()
        payment_line_id = payment.move_id.line_ids.filtered(
            lambda x: x.account_id == self.payable_account
        )
        (invoice_line_id + payment_line_id).reconcile()
        self.assertEqual(invoice_supp_001.payment_state, "paid")
        # We have two move lines

        self.assertEqual(len(payment.res_currency_move_ids.mapped("line_ids")), 2)
        ####
        # Inventory of CC (day 6)
        # -----------------------
        # day 1:
        # * 0 CC @$0,80/CC
        # day 2:
        # * 40 CC @$2,00/CC
        ####
        inventory_balance = self._check_account_balance(self.inventory_account)
        self.assertEqual(inventory_balance, 80.0)
        ####
        # Exchange Rate Profit/Loss
        # -------------------------
        # Profit resulting from exchange rate should be the difference
        # between the cost of the 20 CC @$0,80/CC and 10 @$2,00/CC, and the
        # valuation at the time of paying them ($5,00/CC).
        # That is, a profit of $114,00, added to the prior 126.
        ####
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, -114.0 - 126)

    def test_02(self):
        """Cancels a payment"""
        ####
        # Day 1: Invoice Cust/001 to customer (expressed in CC)
        # Market value of CC (day 1): 1 CC = $0.5
        # * Dr. 100 CC / $50 - Accounts receivable
        # * Cr. 100 CC / $50 - Revenue
        ####
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-01",
                "rate": 2,
            }
        )
        invoice_cust_001 = self.env["account.move"].create(
            {
                "partner_id": self.customer.id,
                "journal_id": self.sale_journal.id,
                "move_type": "out_invoice",
                "currency_id": self.currency_cc.id,
                "company_id": self.company.id,
                "date": time.strftime("%Y") + "-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.env.ref("product.product_product_4").id,
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "name": "product that cost 100",
                            "account_id": self.account_revenue.id,
                        },
                    )
                ],
            }
        )
        invoice_cust_001.action_post()
        self.assertEqual(invoice_cust_001.amount_residual_signed, 50.0)
        aml = invoice_cust_001.mapped("line_ids").filtered(
            lambda x: x.account_id == self.account_revenue
        )
        self.assertEqual(aml.credit, 50.0)
        #####
        # Day 2: Receive payment for half invoice Cust/001 (in CC)
        # -------------------------------------------------------
        # Market value of CC (day 2): 1 CC = $0.8

        # Payment transaction:
        # * Dr. 50 CC / $40 - CC To Inventory (valued at market price
        # at the time of receiving the coins)
        # * Cr. 50 CC / $40 - Accounts Receivable

        # Actual receipt of the coins:
        # * Dr. 50 CC / $40 - CC Inventory (valued at market price
        # at the time of receiving the coins)
        # * Cr. 50 CC / $40 - CC To Inventory
        #####
        # Balance of the To Inventory account should be 0
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, 0.0)
        self.env["res.currency.rate"].create(
            {
                "currency_id": self.currency_cc.id,
                "name": time.strftime("%Y") + "-01-02",
                "rate": 1.25,
            }
        )
        # register payment on invoice
        payment = self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_in"
                ).id,
                "partner_type": "customer",
                "partner_id": self.customer.id,
                "amount": 50,
                "currency_id": self.currency_cc.id,
                "date": time.strftime("%Y") + "-01-02",
                "journal_id": self.cc_journal.id,
            }
        )
        payment.action_post()
        payment.action_cancel()
        # Balance of the To Inventory account should be 0
        to_inventory_balance = self._check_account_balance(self.to_inventory_account)
        self.assertEqual(to_inventory_balance, 0.0)
        # Balance of the Inventory account should be 0
        inventory_balance = self._check_account_balance(self.inventory_account)
        self.assertEqual(inventory_balance, 0.0)
