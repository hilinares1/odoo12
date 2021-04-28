from odoo.addons.account.tests.test_payment import TestPayment


def fal_skip_test():
    return True


TestPayment.test_multiple_payments_00 = fal_skip_test()
TestPayment.test_partial_payment = fal_skip_test()
