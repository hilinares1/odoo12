# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)

TYPE2JOURNAL = { #edit by murha
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}


class PurchaseAdvancePaymentInv(models.TransientModel):
    _name = "purchase.advance.payment.inv"
    _description = "Purchase Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    @api.model
    def _get_advance_payment_method(self):
        if self._count() == 1:
            purchase_obj = self.env['purchase.order']
            order = purchase_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.purchase_method == 'purchase' for line in order.order_line]) or order.invoice_count:
                return 'all'
        return 'received'

    @api.model
    def _default_product_id(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        fal_deposit_product_id = ICPSudo.get_param(
            'fal_purchase_downpayment.fal_deposit_product_id')
        return self.env['product.product'].browse(int(fal_deposit_product_id))

    @api.model
    def _default_deposit_account_id(self):
        return self._default_product_id().property_account_expense_id

    @api.model
    def _default_deposit_taxes_id(self):
        return self._default_product_id().supplier_taxes_id

    @api.model #edit by murha
    def _default_journal(self):
        if self._context.get('default_journal_id', False):
            return self.env['account.journal'].browse(self._context.get('default_journal_id'))
        inv_type = self._context.get('type', 'in_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', [TYPE2JOURNAL[ty] for ty in inv_types if ty in TYPE2JOURNAL]),
            ('company_id', '=', company_id),
        ]
        
        company_currency_id = self.env['res.company'].browse(company_id).currency_id.id
        currency_id = self._context.get('default_currency_id') or company_currency_id
        currency_clause = [('currency_id', '=', currency_id)]
        if currency_id == company_currency_id:
            currency_clause = ['|', ('currency_id', '=', False)] + currency_clause
        return self.env['account.journal'].search(domain + currency_clause, limit=1)

    advance_payment_method = fields.Selection([
        ('received', 'Invoiceable lines'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')],
        string='What do you want to be invoiced?',
        default=_get_advance_payment_method,
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Down Payment Product',
        domain=[('type', '=', 'service')],
        default=_default_product_id)
    amount = fields.Float(
        'Down Payment Amount',
        digits=dp.get_precision('Account'),
        help="The amount to be invoiced in advance, taxes excluded."
    )
    deposit_account_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        help="Account used for deposits",
        default=_default_deposit_account_id
    )
    deposit_taxes_id = fields.Many2many(
        "account.tax",
        string="Vendor Taxes",
        help="Taxes used for deposits",
        default=_default_deposit_taxes_id
    )
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, default=_default_journal)  #edit by murha

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount': 0}}
        return {}

    @api.multi
    def _create_invoice(self, order, po_line, amount, invoice_type):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        invoice = False
        account_id = False
        if self.product_id.id:
            account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id
        if not account_id:
            exp_acc = ir_property_obj.get(
                'property_account_expense_categ_id',
                'product.category'
            )
            account_id = order.fiscal_position_id.map_account(
                exp_acc).id if exp_acc else False
        if not account_id:
            raise UserError(_(
                'There is no expense account defined for this product: "%s".\
                You may have to install a chart of account \
                from Accounting app, settings menu.') %
                (self.product_id.name,))

        # Call the create invoice button, returning result for view, but we take the context
        context = order.action_view_invoice()['context']
        # Prepare data needed for invoice
        partner_id = order.partner_id.id
        new_lines = self.env['account.invoice.line']
        if not order:
            raise UserError(_(
                    'There is no Purchase Order!'
                ))

        # Separate by the type (Downpayment = Only process the dp PO line, Received = Do like usual odoo, Final = Process like usual Odoo + negative amount on the already invoiced)
        if invoice_type == 'downpayment':
            # Because onchange method cannot be called on create method, we redefine it
            if not po_line:
                raise UserError(_(
                        'There is no PO Line!'
                    ))
            data = inv_obj._prepare_invoice_line_from_po_line(po_line)
            context.update(dict(self.env.context, from_purchase_order_change=True))
            if 'quantity' in data:
                data['quantity'] = 1
            new_line = new_lines.create(data)
            if 'invoice_line_tax_ids' in data:
                new_line.invoice_line_tax_ids = [(6, 0, data['invoice_line_tax_ids'])]
            invoice = inv_obj.with_context(context).create({
                'account_id': account_id,
                'partner_id': partner_id,
                'invoice_line_ids': [(6, 0, [new_line.id])],
                'purchase_id': False,
                'journal_id': self.journal_id.id,    #edit by murha
            })

            new_line._set_additional_fields(invoice)
        elif invoice_type == 'final' or invoice_type == 'received':
            context.update(dict(self.env.context, from_purchase_order_change=True))
            inv_data = {
                'account_id': account_id,
                'partner_id': partner_id,
                'purchase_id': order.id,
                'journal_id': self.journal_id.id,   #edit by murha
            }
            if invoice_type == 'final':
                inv_data.update({'deduct_downpayment_purchase': True})
            invoice = inv_obj.with_context(context).create(
                inv_data
            )

        # Make sure all onchange method are called
        invoice._onchange_partner_id()
        invoice._onchange_origin()
        invoice.purchase_order_change()
        invoice._onchange_currency_id()
        invoice._onchange_invoice_line_ids()
        invoice._onchange_journal_id()
        invoice._onchange_payment_term_date_invoice()
        invoice._onchange_cash_rounding()
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    @api.multi
    def create_invoice(self):
        purchase_orders = self.env[
            'purchase.order'
        ].browse(self._context.get('active_ids', []))

        if self.advance_payment_method == 'received':
            invoice = self._create_invoice(purchase_orders, False, False, invoice_type='received')
        elif self.advance_payment_method == 'all':
            invoice = self._create_invoice(purchase_orders, False, False, invoice_type='final')
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                ICPSudo = self.env['ir.config_parameter'].sudo()
                ICPSudo.set_param(
                    "fal_purchase_downpayment.fal_deposit_product_id",
                    self.product_id.id)
            purchase_line = self.env['purchase.order.line']
            for order in purchase_orders:
                if self.advance_payment_method == 'percentage':
                    amount = order.amount_untaxed * self.amount / 100
                else:
                    amount = self.amount
                if self.product_id.purchase_method != 'purchase':
                    raise UserError(_(
                        'The product used to invoice a down payment should \
                        have an invoice policy set to "Ordered quantities".'
                        'Please update your deposit product to \
                        be able to create a deposit invoice.'
                    ))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment \
                        should be of type 'Service'."
                        "Please use another product or update this product."
                    ))
                if order.fiscal_position_id and self.product_id.supplier_taxes_id:
                    tax_ids = order.fiscal_position_id.map_tax(
                        self.product_id.supplier_taxes_id).ids
                else:
                    tax_ids = self.product_id.supplier_taxes_id.ids
                context = {'lang': order.partner_id.lang}
                po_line = purchase_line.create({
                    'name': _('Advance: %s') % (time.strftime('%m %Y'),),
                    'price_unit': amount,
                    'date_planned': order.date_planned,
                    'product_qty': 0.0,
                    'order_id': order.id,
                    'product_uom': self.product_id.uom_id.id,
                    'product_id': self.product_id.id,
                    'taxes_id': [(6, 0, tax_ids)],
                    'fal_is_downpayment': True,
                })
                del context
                invoice = self._create_invoice(order, po_line, amount, invoice_type='downpayment')
        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_deposit_product(self):
        return {
            'name': 'Vendor Down payment',
            'type': 'service',
            'purchase_method': 'purchase',
            'property_account_expense_id': self.deposit_account_id.id,
            'supplier_taxes_id': [(6, 0, self.deposit_taxes_id.ids)],
        }
