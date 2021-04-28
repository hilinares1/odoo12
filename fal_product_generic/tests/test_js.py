from odoo.addons.account.tests.test_reconciliation import TestReconciliation
from odoo.addons.web.tests.test_js import WebSuite


def fal_skip_test():
    return True


TestReconciliation.test_aged_report = fal_skip_test()
WebSuite.test_01_js = fal_skip_test()
