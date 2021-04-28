# -*- encoding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TaxRegisterPayments(models.TransientModel):
    _name = "tax.register.payments"
    _description = 'Tax Register Payment'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money')], string='Payment Type', required=True)
    partner_type = fields.Selection([
        ('customer', 'Customer'), ('supplier', 'Vendor')])
    payment_method_id = fields.Many2one(
        'account.payment.method', string='Payment Method Type', required=True)
    amount = fields.Monetary(string='Payment Amount', required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        required=True,
        default=lambda self: self.env.user.company_id.currency_id)
    payment_date = fields.Date(
        string='Payment Date', default=fields.Date.context_today,
        required=True, copy=False)
    communication = fields.Char(string='Memo')
    journal_id = fields.Many2one(
        'account.journal', string='Payment Journal',
        required=True, domain=['|',('type', 'in', ['bank', 'cash']), ('fal_is_tax_journal', '=', True)])
    company_id = fields.Many2one(
        'res.company', related='journal_id.company_id',
        string='Company', readonly=True)

    @api.multi
    def create_payment(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        tax_note_obj = self.env[active_model].browse(active_ids)
        payment = self.env['account.payment']
        for tax_note in tax_note_obj:
            amount = self.amount
            payment_type = self.payment_type
            account = False
            if payment_type == 'inbound':
                account = self.journal_id.default_credit_account_id
            else:
                account = self.journal_id.default_debit_account_id
            if not account:
                raise UserError(_('Please set account on journal'))
            vals = {
                'journal_id': self.journal_id.id,
                'payment_method_id': self.payment_method_id.id,
                'payment_date': self.payment_date,
                'communication': self.communication,
                'payment_type': payment_type,
                'amount': amount,
                'currency_id': self.currency_id.id,
                'partner_id': tax_note.partner_id.id,
                'partner_type': self.partner_type,
                'fal_tax_note': tax_note_obj.id,
            }
            pay = payment.create(vals)
            for tax_line in tax_note.tax_note_line:
                tax_line.move_line_id.write({
                    'reconciled': True,
                })
            tax_note.write({'state': 'paid', 'payment_id': pay.id})
            pay.post()
            pay.open_payment_matching_screen()
