# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        res = super(AccountInvoice, self).purchase_order_change()
        for invoice_line_id in self.invoice_line_ids:
            if invoice_line_id.purchase_line_id:
                budget_line = invoice_line_id.purchase_line_id.fal_project_budget_line_id
                invoice_line_id.fal_project_budget_line_id = budget_line and budget_line.id
        return res

# end of AccountInvoice()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    fal_project_budget_line_id = fields.Many2one('fal.project.budget.line', "Control Item(s)")

# end of AccountInvoiceLine()
