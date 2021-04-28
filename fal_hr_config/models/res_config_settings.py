# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Partner Management
    module_fal_employee_private_contact = fields.Boolean(
        'Employee Private Contract')

# Extra Tools
    module_fal_calendar_meeting_ext = fields.Boolean(
        'Calendar Meeting Enhancement')

# Human Resource
    module_fal_hr_contract_template = fields.Boolean(
        'Employee Contract Template')
    module_fal_hr_contract_signature = fields.Boolean(
        'Employee Contract Signature')
    module_fal_hr_ext = fields.Boolean(
        'HR Enhancement')
    module_fal_leave = fields.Boolean(
        'Leave Enhancement')
    module_fal_leave_timesheet = fields.Boolean(
        'Leave Timesheet')
    module_fal_meeting_timesheet = fields.Boolean(
        'Meeting Timesheet')

# New HR
    module_fal_hr_payroll_account = fields.Boolean(
        'Payroll Accounting Enhancement')
    module_fal_hr_payroll_messaging = fields.Boolean(
        'Payroll Messaging')
    module_fal_hr_timesheet_analytic_multi_company = fields.Boolean(
        'Hr Timesheet Analytic Multi-Company')
    module_fal_payroll_engine = fields.Boolean(
        'Payroll Engine')
    module_fal_hr_holidays_leave_overlap = fields.Boolean(
        'Holidays Leave Overlap')
