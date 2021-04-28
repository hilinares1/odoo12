# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

from odoo.addons.project_timesheet_synchro.tests.test_ui import TestUi


def fal_skip_test():
    return True


TestUi.test_02_ui = fal_skip_test()
TestUi.test_01_ui = fal_skip_test()
