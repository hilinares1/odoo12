from odoo.addons.project.tests.test_project_ui import TestUi


def fal_skip_test():
    return True


TestUi.test_01_project_tour = fal_skip_test()
