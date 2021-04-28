# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Human Resource
    module_fal_hr_expense = fields.Boolean(
        'HR Expense')
    module_fal_expense_report_document = fields.Boolean(
        'HR Expense Report Document')
    module_fal_period_lock_hr = fields.Boolean(
        'Period Lock For Employee And Manager')
    module_fal_expense_cancel = fields.Boolean(
        'HR Expense Cancel')
