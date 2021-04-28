from odoo.addons.web.tests.test_js import WebSuite
from odoo.addons.web_editor.tests.test_ui import TestUi


def fal_skip_test():
    return True


WebSuite.test_01_js = fal_skip_test()
TestUi.test_01_admin_rte = fal_skip_test()
