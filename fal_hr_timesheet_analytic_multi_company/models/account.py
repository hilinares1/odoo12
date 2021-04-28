# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def _timesheet_preprocess(self, values):
        # In timesheet preprocess, CLuedoo best practice behavior is to
        # Treat Timesheet line company as employee company
        values = super(AccountAnalyticLine, self)._timesheet_preprocess(values)
        if values.get('project_id'):
            if values.get('employee_id'):
                values['company_id'] = self.env['hr.employee'].browse(values.get('employee_id')).company_id and self.env['hr.employee'].browse(values.get('employee_id')).company_id.id or self.env.user.company_id.id
            else:
                values['company_id'] = self.env.user.company_id.id
        return values

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id(self):
        # No need to check company compatibility
        return True

    def _check_sheet_company_id(self, sheet_id):
        # No need to check company compatibility
        self.ensure_one()
        return True

    def _compute_sheet(self):
        """Links the timesheet line to the corresponding sheet"""
        # Full Override
        # Without Thinking the company record
        for timesheet in self:
            if not timesheet.project_id:
                continue
            else:
                sheet = self.env['hr_timesheet.sheet'].search([
                    ('date_end', '>=', timesheet.date),
                    ('date_start', '<=', timesheet.date),
                    ('employee_id', '=', timesheet.employee_id.id),
                    ('state', 'in', ['new', 'draft']),
                ], limit=1)
                if timesheet.sheet_id != sheet:
                    timesheet.sheet_id = sheet


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.constrains('company_id')
    def _check_timesheet_sheet_company_id(self):
        # No need to check company compatibility
        return True
