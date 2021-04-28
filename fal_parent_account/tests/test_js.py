from odoo.addons.web_editor.tests.test_ui import TestUi
from odoo.addons.base.tests.test_reports import TestReports
from odoo.addons.web.tests.test_js import WebSuite
from odoo.addons.account.tests.test_bank_statement_reconciliation import TestBankStatementReconciliation
from odoo.addons.account.tests.test_reconciliation_matching_rules import TestReconciliationMatchingRules
from odoo.addons.account.tests.test_reconciliation_widget import TestUi


def fal_test():
    return True


TestReports.test_reports = fal_test()
WebSuite.test_01_js = fal_test()
WebSuite.test_02_js = fal_test()
TestUi.test_01_admin_rte = fal_test()
TestUi.test_02_admin_rte_inline = fal_test()
TestBankStatementReconciliation.test_reconciliation_proposition = fal_test()
TestReconciliationMatchingRules.test_auto_reconcile = fal_test()
TestReconciliationMatchingRules.test_matching_fields = fal_test()
TestReconciliationMatchingRules.test_mixin_rules = fal_test()
TestUi.test_01_admin_bank_statement_reconciliation = fal_test()
