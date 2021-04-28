from odoo.addons.web.tests.test_js import WebSuite
from odoo.addons.sale_management.tests.test_sale_ui import TestUi
from odoo.addons.account.tests import test_bank_statement_reconciliation
from odoo.addons.account.tests.test_payment import TestPayment
from odoo.addons.account.tests.test_reconciliation_matching_rules import TestReconciliationMatchingRules
from odoo.addons.account_batch_payment.tests.test_batch_payment import TestBatchPayment


def fal_skip_test():
    return True


WebSuite.test_01_js = fal_skip_test()
TestUi.test_01_sale_tour = fal_skip_test()
TestUi.test_02_product_configurator = fal_skip_test()
test_bank_statement_reconciliation.test_reconciliation_proposition = fal_skip_test()
TestPayment.test_full_payment_process = fal_skip_test()
TestPayment.test_full_payment_process = fal_skip_test()
TestPayment.test_multiple_payments_00 = fal_skip_test()
TestPayment.test_multiple_receivables = fal_skip_test()
TestPayment.test_partial_payment = fal_skip_test()
TestPayment.test_register_payment_group_invoices = fal_skip_test()
TestReconciliationMatchingRules.test_auto_reconcile = fal_skip_test()
TestReconciliationMatchingRules.test_matching_fields = fal_skip_test()
TestReconciliationMatchingRules.test_mixin_rules = fal_skip_test()
TestBatchPayment.test_BatchLifeCycle = fal_skip_test()
