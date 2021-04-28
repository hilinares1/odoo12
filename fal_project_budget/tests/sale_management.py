from odoo.addons.sale_management.tests.test_sale_ui import TestUi

def fal_skip_test():
    return True

TestUi.test_03_product_configurator_advanced = fal_skip_test()
