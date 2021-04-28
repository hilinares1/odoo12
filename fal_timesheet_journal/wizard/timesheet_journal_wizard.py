from odoo import models, fields, api


class TimesheetJournal(models.TransientModel):
    _name = "timesheet.journal.wizard"

    product_id = fields.Many2one('product.product', string="Product")
    account_expense_id = fields.Many2one(
        'account.account', string="Expense Account",
        domain=[('deprecated', '=', False)])
    check_expense_account = fields.Boolean(compute='_check_product_account')
    check_product = fields.Boolean(compute='_check_product_account')

    @api.depends('product_id')
    def _check_product_account(self):
        ctx = dict(self._context)
        active_ids = ctx.get('active_ids')
        sheet_ids = self.env['hr_timesheet.sheet'].browse(active_ids)
        for sheet in sheet_ids:
            product = sheet.employee_id.fal_product_id
            if product:
                self.check_product = True
            if product.product_tmpl_id._get_product_accounts()['expense'] or self.product_id.product_tmpl_id._get_product_accounts()['expense']:
                self.check_expense_account = True

    def set_product_account(self):
        ctx = dict(self._context)
        active_ids = ctx.get('active_ids')
        sheet_ids = self.env['hr_timesheet.sheet'].browse(active_ids)
        for sheet in sheet_ids:
            if not self.check_product:
                sheet.employee_id.fal_product_id = self.product_id.id
            if not self.check_expense_account:
                self.product_id.property_account_expense_id = self.account_expense_id.id
            sheet.action_sheet_move_create()
