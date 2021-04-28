# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_repr


class FalInvoiceLineAnalyticAccountChange(models.TransientModel):
    _name = "fal.invoice.line.analytic.account.change"
    _description = "Invoice Line Analytic Account Change"

    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account'
    )

    @api.model
    def default_get(self, fields):
        res = super(FalInvoiceLineAnalyticAccountChange, self).default_get(
            fields)
        if self.env.context.get('active_id'):
            res['account_analytic_id'] = self.env[
                'account.invoice.line'].browse(
                self.env.context['active_id']).account_analytic_id.id
        return res

    @api.multi
    def changeAnalayticAccount(self):
        invoice_line_id = self.env['account.invoice.line'].browse(
            self._context.get('active_id'))
        old_analytic_acc = invoice_line_id.account_analytic_id.name
        invoice_line_id.account_analytic_id = self.account_analytic_id and self.account_analytic_id.id or False

        # We get the invoice Decimal to check, if not found check company currency lastly let's say default is 2
        precision = invoice_line_id.currency_id and invoice_line_id.currency_id.decimal_places or invoice_line_id.company_currency_id and invoice_line_id.company_currency_id.decimal_places or 2

        move_ids = invoice_line_id.invoice_id.move_id.line_ids.filtered(
            lambda l: l.product_id.id == invoice_line_id.product_id.id and
            l.quantity == invoice_line_id.quantity and (
                float_round(abs(l.debit), precision_digits=precision) == float_round(abs(invoice_line_id.price_subtotal), precision_digits=precision) or
                float_round(abs(l.credit), precision_digits=precision) == float_round(abs(invoice_line_id.price_subtotal), precision_digits=precision)))

        if move_ids:
            move_ids.write({
                'analytic_account_id': self.account_analytic_id and
                self.account_analytic_id.id or False
            })
            move_ids.create_analytic_lines()
        else:
            raise UserError(
                _('You cannot change the Analytic Account for this transaction, \
                    Please contact your Account Advisor'))

        # create message on invoice
        invoice_id = invoice_line_id.invoice_id
        message = _("""
            <p>Your invoice line analytic account has been change : </p>
            <ul>
            """)
        message += "<li>"
        message += _("From : ")
        message += old_analytic_acc or ''
        message += "<li>"
        message += _("To : ")
        message += self.account_analytic_id and self.account_analytic_id.name or ""
        message += "</li>"
        message += "</ul>"

        invoice_id.message_post(
            subject=_("Analytic Account Change"),
            body=message,
        )

        return {'type': 'ir.actions.act_window_close'}

# End of FalInvoiceLineAnalyticAccountChange()
