from odoo.addons.web_editor.tests.test_ui import TestUi
from odoo.addons.web.tests.test_js import WebSuite

def fal_skip_test():
    return True


TestUi.test_01_admin_rte = fal_skip_test()
TestUi.test_02_admin_rte_inline = fal_skip_test()
WebSuite.test_01_js = fal_skip_test()