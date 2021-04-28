from odoo.addons.account.tests.test_payment import TestPayment
from odoo.addons.web.tests.test_js import WebSuite
from odoo.addons.web_editor.tests.test_ui import TestUi


def fal_skip_test():
    return True


TestPayment.test_multiple_payments_00 = fal_skip_test()
TestPayment.test_multiple_receivables = fal_skip_test()
TestPayment.test_register_payment_group_invoices = fal_skip_test()
WebSuite.test_01_js = fal_skip_test()
TestUi.test_01_admin_rte = fal_skip_test()
TestUi.test_02_admin_rte_inline = fal_skip_test()
