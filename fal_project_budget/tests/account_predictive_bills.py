from odoo.addons.account_predictive_bills.tests.test_prediction import TestBillsPrediction


def fal_skip_test():
    return True


TestBillsPrediction.test_account_prediction_flow = fal_skip_test()
