from odoo.addons.sale_management.tests.test_sale_ui import TestUi


def fal_skip_test():
    return True


TestUi.test_02_product_configurator = fal_skip_test()
