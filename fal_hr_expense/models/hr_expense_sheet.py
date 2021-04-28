# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    # Apporval N+1 ==============================
    @api.multi
    def _get_can_approve(self):
        for exp in self:
            exp.fal_can_approve = False
            user = self.env['res.users'].browse(self._uid)
            subordinate_obj = self.env['hr.employee'].search([
                ('id', 'child_of', user.employee_ids.ids),
                ('id', 'not in', user.employee_ids.ids)])
            if user.has_group('fal_hr_expense.group_hr_expense_user_responsible'):
                exp.fal_can_approve = True
            else:
                if exp.employee_id.id in subordinate_obj.ids:
                    exp.fal_can_approve = True

    # Additional Info
    date_submit = fields.Date('Submit Date')
    number = fields.Char(string='Number')
    note = fields.Text("Notes")
    date_confirm = fields.Date('Confirmation Date', index=True, copy=False, help="Date of the confirmation of the sheet expense. It's filled when the button Confirm is pressed.")
    date_valid = fields.Date('Validation Date', index=True, copy=False, help="Date of the acceptation of the sheet expense. It's filled when the button Accept is pressed.")
    user_valid = fields.Many2one('res.users', 'Validation By', readonly=True, copy=False)
    fal_parent_id = fields.Many2one('hr.employee', related='employee_id.parent_id', string='Parent', store=True)

    # Total Summary
    tax = fields.Monetary(
        compute="_compute_amount_total_withtax_accepted",
        string='tax Total Amount',
        digits=dp.get_precision('Account'),
        store=1
    )
    notax = fields.Monetary(
        compute="_compute_amount_total_withtax_accepted",
        string='Untaxed Total Amount',
        digits=dp.get_precision('Account'),
        store=1)
    withtax = fields.Monetary(
        compute="_compute_amount_total_withtax_accepted",
        string='Withtax Total Amount',
        digits=dp.get_precision('Account'),
        store=1
    )
    accepted = fields.Monetary(
        compute="_compute_amount_total_withtax_accepted",
        string='Accepted Total Amount',
        digits=dp.get_precision('Account'),
        store=1)

    # State
    is_all_paid = fields.Boolean(
        compute='get_all_paid',
        string='All Paid'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Waiting Payment'),
        ('done', 'Paid'),
        ('to_be_defined', 'To Be Defined'),
        ('cancel', 'Refused'),
    ], string='Status', index=True, readonly=True, track_visibility='onchange', copy=False, default='submit', required=True, help='Expense Report State')

    # Security
    fal_can_approve = fields.Boolean(
        compute="_get_can_approve", string="Can Approve", default=False)

    # Rename String to Accounting Date
    accounting_date = fields.Date(string="Accounting Date")

    @api.multi
    @api.depends('expense_line_ids','expense_line_ids.tax_ids','expense_line_ids.fal_withtax_price','expense_line_ids.fal_accepted_amount','expense_line_ids.fal_withouttax_price')
    def _compute_amount_total_withtax_accepted(self):
        for expense in self:
            withtax_total = 0.0
            accepted = 0.0
            tax = 0.0
            notax = 0.0
            for line in expense.expense_line_ids:
                withtax_total += line.fal_withtax_price
                accepted += line.fal_accepted_amount
                tax += line.fal_total_tax
                notax += line.fal_withouttax_price
            expense.withtax = withtax_total
            expense.accepted = accepted
            expense.tax = tax
            expense.notax = notax

    @api.multi
    @api.depends('expense_line_ids', 'expense_line_ids.state')
    def get_all_paid(self):
        for sheet in self:
            sheet.is_all_paid = True
            if any(
                expense.state != 'done' for expense in sheet.expense_line_ids
            ):
                sheet.is_all_paid = False

    @api.model
    def create(self, vals):
        # Add the followers at creation, so they can be notified
        vals['number'] = self.env['ir.sequence'].next_by_code(
            'expense.sheet') or ''
        sheet = super(HrExpenseSheet, self).create(vals)
        sheet.activity_update()
        return sheet
