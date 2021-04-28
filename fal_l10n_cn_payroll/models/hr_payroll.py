#-*- coding:utf-8 -*-
from datetime import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from odoo import models


class Employee(models.Model):
    _inherit = 'hr.employee'

    def get_employeecurrentyear_payslip(self):
        result = []
        for slip in self.slip_ids.filtered(lambda slip: slip.state == 'done' and str(datetime.strptime(slip.date_from, DEFAULT_SERVER_DATE_FORMAT).year) == str(datetime.today().strftime("%Y"))):
            result.append(slip)
        return result
