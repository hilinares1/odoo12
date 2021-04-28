# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _compute_comment(self):
        taxes = []
        str_tax = ''
        for invoice in self:
            for invoice_line in invoice.invoice_line_ids:
                for tax in invoice_line.invoice_line_tax_ids:
                    if tax not in taxes:
                        taxes.append(tax)
                        tax_comment_template = self.env['fal.comment.template'].search([['tax_ids', '=', tax.id]])
                        str_comment = ""
                        for comment in tax_comment_template:
                            str_comment += comment.name + ', '
                        str_tax += tax and str_comment or ""
            invoice.fal_tax_comment = str_tax

    fal_tax_comment = fields.Text(
        string="Tax Comment", compute='_compute_comment')
