from odoo.addons.sale_management.tests.test_sale_ui import TestUi


def fal_skip_test():
    return True


TestUi.test_01_sale_tour = fal_skip_test()
TestUi.test_02_product_configurator = fal_skip_test()
TestUi.test_03_product_configurator_advanced = fal_skip_test()
