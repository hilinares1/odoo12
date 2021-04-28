# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(account_register_payments, self)._onchange_journal()
        if self.journal_id:
            for wizard_line in self.payment_wizard_line_ids:
                wizard_line.journal_id = self.journal_id.id
                self.payment_method_id = wizard_line.payment_method_id and wizard_line.payment_method_id[0]
        return res

    @api.onchange('payment_date')
    def _onchange_payment_date(self):
        if self.payment_date:
            for wizard_line in self.payment_wizard_line_ids:
                wizard_line.payment_date = self.payment_date

    @api.onchange('payment_method_id')
    def _onchange_payment_method_id(self):
        if self.payment_method_id:
            for wizard_line in self.payment_wizard_line_ids:
                pay_type = self.payment_method_id.payment_type
                if wizard_line.payment_type == pay_type:
                    wizard_line.payment_method_id = self.payment_method_id.id

    @api.model
    def _default_payment_wizard_line_ids(self):
        if self.env.context.get('active_ids', False):
            active_ids = self.env.context.get('active_ids')
            temp = []
            for invoices in self.env['account.invoice'].browse(active_ids):
                currency = False
                journal = self.env['account.journal'].search(
                    [('type', '=', 'bank')], limit=1)

                if any(inv.currency_id != invoices[0].currency_id
                       for inv in invoices):
                    raise UserError(_(
                        "In order to pay multiple invoices at once, "
                        "they must use the same currency."))
                for invoice in invoices:
                    if invoice.state != 'open':
                        raise UserError(_(
                            "You can only register payments for open invoices"
                        ))
                    currency = invoice.currency_id.id

                payment_method = self.env['account.payment.method'].search(
                    [
                        (
                            'payment_type',
                            '=',
                            invoices.residual > 0 and 'inbound' or 'outbound')
                    ], limit=1)
                communication = False
                list_ref = invoices.filtered('reference').mapped('reference')
                if list_ref:
                    communication = ','.join(list_ref)
                inv_type = MAP_INVOICE_TYPE_PAYMENT_SIGN[invoice.type]
                total_amount = invoice.residual * inv_type
                temp.append((0, 0, {
                    'partner_id': invoices.commercial_partner_id.id or invoices.partner_id.id,
                    'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
                    'amount': abs(invoices.residual),
                    'currency_id': currency,
                    'payment_type': total_amount > 0 and 'inbound' or 'outbound',
                    'payment_date': fields.date.today(),
                    'invoice_ids': [(6, 0, invoices.ids)],
                    'fal_number': invoices and invoices[0].number,
                    'journal_id': journal and journal[0].id,
                    'payment_method_id': payment_method and payment_method[0].id,
                    'communication': communication,
                }))
        return temp

    @api.multi
    def create_multi_payment(self):
        fal_multi_payment_number = self.env['ir.sequence'].next_by_code(
            'preparation.payment.fwa') or 'New'
        payment_ids = []
        for wizard_line in self.payment_wizard_line_ids:
            res = wizard_line.with_context({'active_id': wizard_line.id}).fal_create_payments()
            self.env['account.payment'].browse(res['res_id']).write({'fal_multi_payment_number': fal_multi_payment_number})
            payment_ids.append(res['res_id'])
        batch = self.env['account.batch.payment'].create({
            'journal_id': self[0].journal_id.id,
            'payment_ids': [(6, 0, payment_ids)],
            'payment_method_id': self[0].payment_method_id.id,
            'batch_type': self[0].payment_type,
        })
        for bp in batch.payment_ids:
            for invoice in bp.invoice_ids:
                invoice.write({'reference': batch.name})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def create_payments(self):
        if self.fal_split_multi_payment:
            self.create_multi_payment()
        else:
            super(account_register_payments, self).create_payments()

    payment_wizard_line_ids = fields.One2many(
        'fal.multi.payment.wizard',
        'register_payments_id', 'Payment List', default=_default_payment_wizard_line_ids)
    fal_split_multi_payment = fields.Boolean(
        string="Split payments for each invoice", default=True)


class fal_multi_payment_wizard(models.TransientModel):
    _name = "fal.multi.payment.wizard"
    _description = "Multi Payment Wizard"

    register_payments_id = fields.Many2one(
        'account.register.payments', 'Payment List')
    partner_id = fields.Many2one('res.partner', string='Partner')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type', required=True)
    payment_date = fields.Date(string='Payment Date', default=fields.Date.context_today, required=True, copy=False)
    invoice_ids = fields.Many2many('account.invoice', string='Invoices', copy=False)
    fal_number = fields.Char(string='Number')
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method",
        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n"\
        "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n"\
        "Check: Pay bill by check and print it from Odoo.\n"\
        "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit, module account_batch_payment must be installed.\n"\
        "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    communication = fields.Char(string='Memo')

    @api.multi
    def _prepare_payment_vals(self, invoices):
        amount = self.amount
        payment_type = self.payment_type
        bank_account = invoices and invoices[0].partner_bank_id or self.register_payments_id.partner_bank_account_id
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'partner_bank_account_id': bank_account.id,
        }

    @api.multi
    def get_payments_vals(self):
        return [self._prepare_payment_vals(self.invoice_ids)]

    @api.multi
    def fal_create_payments(self):
        Payment = self.env['account.payment']
        payments = Payment
        for payment_vals in self.get_payments_vals():
            payments += Payment.create(payment_vals)
        payments.post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals
