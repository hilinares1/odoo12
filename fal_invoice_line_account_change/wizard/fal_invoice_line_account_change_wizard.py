# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_repr


class FalInvoiceLineAccountChange(models.TransientModel):
    _name = "fal.invoice.line.account.change"
    _description = "Invoice Line Account Change"

    account_id = fields.Many2one(
        'account.account',
        string='Account',
        required=True
    )
    account_id_from = fields.Many2one(
        'account.account',
        string='Account From',
    )

    @api.model
    def default_get(self, fields):
        res = super(FalInvoiceLineAccountChange, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['account_id_from'] = self.env['account.invoice.line'].browse(
                self.env.context['active_id']).account_id.id
        return res

    @api.multi
    def changeAccount(self):
        invoice_line_id = self.env['account.invoice.line'].browse(
            self._context.get('active_id'))
        invoice_line_id.account_id = self.account_id and self.account_id.id
        account_invoice_line_from = self.account_id_from.code + \
            " " + str(self.account_id_from.name)
        # We get the invoice Decimal to check, if not found check company currency lastly let's say default is 2
        precision = invoice_line_id.currency_id and invoice_line_id.currency_id.decimal_places or invoice_line_id.company_currency_id and invoice_line_id.company_currency_id.decimal_places or 2

        if invoice_line_id.invoice_id.currency_id == invoice_line_id.invoice_id.journal_id.company_id.currency_id: #edit by murha
            move_line_ids = invoice_line_id.invoice_id.move_id.line_ids.filtered(
                lambda l: l.product_id.id == invoice_line_id.product_id.id and
                l.quantity == invoice_line_id.quantity and (
                    float_round(l.debit, precision_digits=precision) == abs(float_round(invoice_line_id.price_subtotal, precision_digits=precision)) or
                    float_round(l.credit, precision_digits=precision) == abs(float_round(invoice_line_id.price_subtotal, precision_digits=precision))))
        else: #edit by murha
            move_line_ids = invoice_line_id.invoice_id.move_id.line_ids.filtered(
                lambda l: l.product_id.id == invoice_line_id.product_id.id and
                l.quantity == invoice_line_id.quantity and (
                    float_round(invoice_line_id.invoice_id.journal_id.company_id.currency_id._convert(l.debit, invoice_line_id.currency_id, invoice_line_id.invoice_id.journal_id.company_id, invoice_line_id.invoice_id.date_invoice), precision_digits=precision) == abs(float_round(invoice_line_id.price_subtotal, precision_digits=precision)) or
                    float_round(invoice_line_id.invoice_id.journal_id.company_id.currency_id._convert(l.credit, invoice_line_id.currency_id, invoice_line_id.invoice_id.journal_id.company_id, invoice_line_id.invoice_id.date_invoice), precision_digits=precision) == abs(float_round(invoice_line_id.price_subtotal, precision_digits=precision))))

        if move_line_ids:
            move_line_ids.mapped('move_id').button_cancel()
            move_line_ids.write({
                'account_id': self.account_id and self.account_id.id
            })
            move_line_ids.mapped('move_id').post()
        else:
            raise UserError(
                _('You cannot change the Account for this transaction, \
                    Please contact your Account Advisor'))
        # create message on invoice
        invoice_id = invoice_line_id.invoice_id
        message = _("""
            <p>Your invoice line account has been change : </p>
            <ul>
            """)
        message += "<li>"
        message += _("From : ")
        message += account_invoice_line_from
        message += "</li>"
        message += "<li>"
        message += _("To : ")
        message += self.account_id and self.account_id.display_name
        message += "</li>"
        message += "</ul>"

        invoice_id.message_post(
            subject=_("Account Change"),
            body=message,
        )
        return {'type': 'ir.actions.act_window_close'}

# End of FalInvoiceLineAccountChange
