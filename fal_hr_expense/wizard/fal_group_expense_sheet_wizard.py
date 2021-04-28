# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from datetime import datetime


class fal_group_expense_sheet_wizard(models.TransientModel):
    _name = 'fal.group.expense.sheet.wizard'
    _description = "Group Expense Sheet"

    sheet_id = fields.Many2one('hr.expense.sheet', 'Expense Sheet')
    link_to_existing_expense_sheet = fields.Boolean(
        'Link to Existing Expense Sheet')
    name = fields.Char('Description', size=128)

    @api.multi
    def action_group_expense_sheet(self):
        self.ensure_one()
        expense_obj = self.env['hr.expense.sheet']
        expense_line_obj = self.env['hr.expense']
        imd_obj = self.env['ir.model.data']
        expense_ids = expense_line_obj.browse(
            self.env.context.get('active_ids'))
        expensesheet_id = False

        if any(expense.state != 'draft' or expense.sheet_id for expense in expense_ids):
            raise UserError(_("You cannot report twice the same line!"))
        if len(expense_ids.mapped('employee_id')) > 1:
            raise UserError(_(
                'You cannot group expense on different employee!'))
        if len(expense_ids.mapped('currency_id')) > 1:
            raise UserError(_(
                'You cannot group expense on different currency!'))

        if self.sheet_id and self.link_to_existing_expense_sheet:
            expense_ids.write({
                'sheet_id': self.sheet_id.id,
            })
            expensesheet_id = self.sheet_id.id
        else:
            expensesheet_create_id = expense_obj.create({
                'name': self.name,
                'employee_id': expense_ids[0].employee_id.id,
                'company_id': expense_ids[0].company_id.id,
                'currency_id': expense_ids[0].currency_id.id,
                'date_submit': datetime.now(),
                'department_id': expense_ids[0].employee_id.department_id.id,
            })
            expense_ids.write({
                'sheet_id': expensesheet_create_id.id,
            })
            expensesheet_id = expensesheet_create_id.id
        action = imd_obj.xmlid_to_object(
            'hr_expense.action_hr_expense_sheet_my_all')
        list_view_id = imd_obj.xmlid_to_res_id(
            'hr_expense.view_hr_expense_sheet_tree')
        form_view_id = imd_obj.xmlid_to_res_id(
            'hr_expense.view_hr_expense_sheet_form')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'domain': "[('id','in',%s)]" % [expensesheet_id],
        }

# end of fal_group_expense_sheet_wizard()
