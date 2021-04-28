# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Human Resource
    module_fal_timesheet_ext = fields.Boolean(
        'Timesheet Extention')
    module_fal_timesheet_minimum_hour = fields.Boolean(
        'Timesheet Minimum Hour')
    module_fal_timesheet_template = fields.Boolean(
        'Timesheet Template')
    module_hr_timesheet_sheet = fields.Boolean(
        'Timesheet Sheet')
    module_fal_timesheet_sheet_menu = fields.Boolean(
        'Timesheet Sheet Menu')
    module_fal_timesheet_invoice_ext = fields.Boolean(
        'Timesheet Invoice')
# Accounting
    module_fal_timesheet_journal = fields.Boolean(
        'Timesheet Journal')