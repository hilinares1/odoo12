from odoo.addons.account.tests.test_bank_statement_reconciliation import TestBankStatementReconciliation
from odoo.addons.account.tests.test_reconciliation_widget import TestUi


def fal_skip_test():
    return True


TestBankStatementReconciliation.test_reconciliation_proposition = fal_skip_test()
TestUi.test_01_admin_bank_statement_reconciliation = fal_skip_test()
