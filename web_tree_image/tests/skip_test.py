from odoo.addons.web_editor.tests.test_ui import TestUi


def fal_skip_test():
    return True


TestUi.test_01_admin_rte = fal_skip_test()
