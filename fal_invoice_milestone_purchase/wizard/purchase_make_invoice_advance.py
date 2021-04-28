import time
from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare


class PurchaseAdvancePaymentInv(models.TransientModel):
    _inherit = "purchase.advance.payment.inv"
    # from falinwa module fal_purchase_downpayment

    @api.multi
    def _create_invoice(self, order, po_line, amount, invoice_type):
        invoice = super(PurchaseAdvancePaymentInv, self)._create_invoice(order, po_line, amount, invoice_type)
        original_po_line = self._context.get("po_line", False)
        original_term_line = self._context.get("term_line", False)
        if original_po_line:
            for invoice_line in invoice.invoice_line_ids:
                for purchase_order_line in invoice_line.purchase_line_id:
                    if purchase_order_line.product_id == self.product_id:
                        new_name = original_po_line.product_id.display_name or "" + " - "
                        new_name += purchase_order_line.name
                        # If there is description on term line
                        if original_term_line and original_term_line.description:
                            new_name += " - " + original_term_line.description
                        purchase_order_line.name = new_name
        # Add Invoice in the Term Line
        if original_term_line:
            original_term_line.invoice_id = invoice.id
        return invoice

    # duplicate function odoo to split downpayment
    @api.multi
    def _fal_milestone_create_invoice(self, order, po_line, amount, invoice_type):
        inv_obj = self.env['account.invoice']
        ir_property_obj = self.env['ir.property']
        ctx = dict(self._context)
        original_term_line = ctx.get('term_line')
        original_po_line = ctx.get('po_line')

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

        if original_po_line:
            for invoice_line in invoice.invoice_line_ids:
                for purchase_order_line in invoice_line.purchase_line_id:
                    if purchase_order_line.product_id == self.product_id:
                        new_name = original_po_line.product_id.display_name or "" + " - "
                        new_name += purchase_order_line.name
                        # If there is description on term line
                        if original_term_line and original_term_line.description:
                            new_name += " - " + original_term_line.description
                        purchase_order_line.name = new_name
        # Add Invoice in the Term Line
        if original_term_line:
            original_term_line.invoice_id = invoice.id

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

    # duplicate function odoo to split downpayment
    @api.multi
    def fal_milestone_create_invoices(self):
        purchase_orders = self.env[
            'purchase.order'
        ].browse(self._context.get('active_ids', []))
        ctx = dict(self._context)

        if self.advance_payment_method == 'received':
            invoice = self._create_invoice(purchase_orders, False, False,invoice_type='received')
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
                    amount = ctx.get('po_line').price_subtotal * self.amount / 100
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
                self._fal_milestone_create_invoice(order, po_line, amount, invoice_type='downpayment')
        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

# end of FalInvoiceMilestoneLine()
