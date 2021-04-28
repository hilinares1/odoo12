# -*- coding:utf-8 -*-
from odoo import fields, models, api, _


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ["hr.payslip", "mail.thread"]

    state = fields.Selection(track_visibility='onchange')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
