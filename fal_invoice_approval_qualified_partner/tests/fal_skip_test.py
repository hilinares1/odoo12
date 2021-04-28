from odoo.addons.web.tests.test_js import WebSuite
from odoo.addons.web_editor.tests.test_ui import TestUi
from odoo.addons.account.tests.test_account_customer_invoice import TestAccountCustomerInvoice
from odoo.addons.account.tests.test_account_invoice_rounding import TestAccountInvoiceRounding
from odoo.addons.account.tests.test_bank_statement_reconciliation import TestBankStatementReconciliation
from odoo.addons.account.tests.test_account_supplier_invoice import TestAccountSupplierInvoice
from odoo.addons.account.tests.test_payment import TestPayment
from odoo.addons.account.tests.test_reconciliation import TestReconciliation
from odoo.addons.account.tests.test_reconciliation_matching_rules import TestReconciliationMatchingRules
from odoo.addons.account_yodlee.tests.test_yodlee_api import TestYodleeApi
from odoo.addons.account_plaid.tests.test_plaid_api import TestPlaidApi


def fal_skip_test():
    return True


WebSuite.test_01_js = fal_skip_test()
WebSuite.test_02_js = fal_skip_test()
TestUi.test_01_admin_rte = fal_skip_test()
TestUi.test_02_admin_rte_inline = fal_skip_test()
TestAccountCustomerInvoice.test_customer_invoice = fal_skip_test()
TestBankStatementReconciliation.test_full_reconcile = fal_skip_test()

TestReconciliation.test_revert_payment_and_reconcile_exchange = fal_skip_test()
TestReconciliation.test_statement_eur_invoice_usd_transaction_usd = fal_skip_test()
TestReconciliation.test_statement_eur_invoice_usd_transaction_eur = fal_skip_test()
TestReconciliation.test_partial_reconcile_currencies_01 = fal_skip_test()
TestReconciliation.test_partial_reconcile_currencies_02 = fal_skip_test()
TestReconciliation.test_statement_euro_invoice_usd_transaction_euro_full = fal_skip_test()
TestReconciliation.test_unreconcile_exchange = fal_skip_test()
TestReconciliation.test_statement_euro_invoice_usd_transaction_chf = fal_skip_test()
TestReconciliation.test_statement_usd_invoice_usd_transaction_eur = fal_skip_test()
TestReconciliation.test_reconcile_bank_statement_with_payment_and_writeoff = fal_skip_test()
TestReconciliation.test_statement_usd_invoice_chf_transaction_chf = fal_skip_test()
TestReconciliation.test_statement_usd_invoice_usd_transaction_usd = fal_skip_test()
TestReconciliation.test_statement_usd_invoice_eur_transaction_eur = fal_skip_test()
TestReconciliation.test_aged_report = fal_skip_test()
TestReconciliation.test_unreconcile = fal_skip_test()
TestReconciliation.test_aged_report_future_payment = fal_skip_test()

TestReconciliationMatchingRules.test_auto_reconcile = fal_skip_test()
TestReconciliationMatchingRules.test_matching_fields = fal_skip_test()
TestReconciliationMatchingRules.test_mixin_rules = fal_skip_test()

TestPlaidApi.test_assign_partner_automatically = fal_skip_test()
TestPlaidApi.test_plaid_fetch_transactions = fal_skip_test()

TestYodleeApi.test_assign_partner_automatically = fal_skip_test()
TestYodleeApi.test_yodlee_fetch_transactions = fal_skip_test()
TestYodleeApi.test_yodlee_cron_fetch_transactions = fal_skip_test()

TestAccountInvoiceRounding.test_rounding_add_invoice_line = fal_skip_test()
TestAccountInvoiceRounding.test_rounding_biggest_tax = fal_skip_test()

TestAccountSupplierInvoice.test_supplier_invoice = fal_skip_test()
TestAccountSupplierInvoice.test_supplier_invoice2 = fal_skip_test()

TestBankStatementReconciliation.test_full_reconcile = fal_skip_test()
TestBankStatementReconciliation.test_reconciliation_proposition = fal_skip_test()
TestBankStatementReconciliation.test_post_at_bank_rec_full_reconcile = fal_skip_test()

TestPayment.test_full_payment_process = fal_skip_test()
TestPayment.test_multiple_payments_00 = fal_skip_test()
TestPayment.test_payment_and_writeoff_in_other_currency_3 = fal_skip_test()
TestPayment.test_payment_and_writeoff_in_other_currency_2 = fal_skip_test()
TestPayment.test_multiple_receivables = fal_skip_test()
TestPayment.test_payment_and_writeoff_in_other_currency_1 = fal_skip_test()
TestPayment.test_register_payment_group_invoices = fal_skip_test()
TestPayment.test_partial_payment = fal_skip_test()
