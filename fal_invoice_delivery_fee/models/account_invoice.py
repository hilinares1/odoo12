from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        res['is_delivery_fees'] = line.is_delivery_fees,
        res['fal_manual_delivery_fee'] = line.fal_manual_delivery_fee
        if line.is_delivery_fees:
            res.update({'sequence': 999})
        return res


class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"

    @api.multi
    @api.depends('is_delivery_fees', 'price_unit', 'quantity', 'invoice_line_tax_ids', 'discount', 'invoice_id')
    def _get_fapiao_unit_price(self):
        for invoice_line_id in self:
            acline = invoice_line_id.name
            if acline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = invoice_line_id.price_subtotal_vat
                subtotal_delivery_fee = 0.00
                unit_price = invoice_line_id.price_unit * (1 - (invoice_line_id.discount or 0.0) / 100.0)
                qty = invoice_line_id.quantity
                tin = []
                manual = False
                for tax_id in invoice_line_id.invoice_line_tax_ids:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if invoice_line_id.invoice_id:
                    for invoice_lie_id_in_invoice in invoice_line_id.invoice_id.invoice_line_ids:
                        if invoice_lie_id_in_invoice.is_delivery_fees:
                            subtotal_delivery_fee += invoice_lie_id_in_invoice.price_subtotal_vat
                        total += invoice_lie_id_in_invoice.price_subtotal_vat
                        if invoice_lie_id_in_invoice.fal_manual_delivery_fee:
                            manual = True
                    if invoice_line_id.fal_manual_delivery_fee or manual:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal:
                                if tin:
                                    fapiao_unit_price = unit_price + invoice_line_id.fal_manual_delivery_fee / qty
                                else:
                                    taxes_delivery_fee = invoice_line_id.invoice_line_tax_ids.compute_all(invoice_line_id.fal_manual_delivery_fee, None, 1, None, invoice_line_id.invoice_id.partner_id)
                                    cur_delivery_fee = invoice_line_id.invoice_id.currency_id
                                    delivery_fee_with_vat = cur_delivery_fee.round(taxes_delivery_fee['total_included'])
                                    fapiao_unit_price = invoice_line_id.price_subtotal_vat / qty + delivery_fee_with_vat / qty
                    else:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal:
                                if tin:
                                    fapiao_unit_price = unit_price + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                                else:
                                    fapiao_unit_price = invoice_line_id.price_subtotal_vat / qty + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                else:
                    fapiao_unit_price = unit_price
                invoice_line_id.fapiao_unit_price_vat = fapiao_unit_price

    @api.multi
    @api.depends('is_delivery_fees', 'price_unit', 'quantity', 'invoice_line_tax_ids', 'discount', 'invoice_id')
    def _get_fapiao_sub_total(self):
        for invoice_line_id in self:
            acline = invoice_line_id.name
            if acline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = invoice_line_id.price_subtotal
                subtotal_delivery_fee = 0.00
                unit_price = invoice_line_id.price_unit * (1 - (invoice_line_id.discount or 0.0) / 100.0)
                qty = invoice_line_id.quantity
                manual = False
                if invoice_line_id.invoice_id:
                    for invoice_lie_id_in_invoice in invoice_line_id.invoice_id.invoice_line_ids:
                        if invoice_lie_id_in_invoice.is_delivery_fees:
                            subtotal_delivery_fee += invoice_lie_id_in_invoice.price_subtotal
                        total += invoice_lie_id_in_invoice.price_subtotal
                        if invoice_lie_id_in_invoice.fal_manual_delivery_fee:
                            manual = True
                    if invoice_line_id.fal_manual_delivery_fee or manual:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = unit_price + invoice_line_id.fal_manual_delivery_fee / qty
                    else:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = unit_price + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                else:
                    fapiao_unit_price = unit_price
                totalex = fapiao_unit_price * qty
                tin = []
                for tax_id in invoice_line_id.invoice_line_tax_ids:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if tin:
                    if invoice_line_id.fal_manual_delivery_fee:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = invoice_line_id.price_subtotal + invoice_line_id.fal_manual_delivery_fee
                    else:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = invoice_line_id.price_subtotal + subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee)
                invoice_line_id.fapiao_subtotal = totalex

    @api.multi
    @api.depends('is_delivery_fees', 'price_unit', 'quantity', 'invoice_line_tax_ids', 'discount', 'invoice_id')
    def _get_fapiao_sub_total_vat(self):
        for invoice_line_id in self:
            acline = invoice_line_id.name
            if acline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = invoice_line_id.price_subtotal_vat
                subtotal_delivery_fee = 0.00
                unit_price = invoice_line_id.price_unit * (1 - (invoice_line_id.discount or 0.0) / 100.0)
                qty = invoice_line_id.quantity
                manual = False
                if invoice_line_id.invoice_id:
                    for invoice_lie_id_in_invoice in invoice_line_id.invoice_id.invoice_line_ids:
                        if invoice_lie_id_in_invoice.is_delivery_fees:
                            subtotal_delivery_fee += invoice_lie_id_in_invoice.price_subtotal_vat
                        total += invoice_lie_id_in_invoice.price_subtotal_vat
                        if invoice_lie_id_in_invoice.fal_manual_delivery_fee:
                            manual = True
                    taxes_delivery_fee = invoice_line_id.invoice_line_tax_ids.compute_all(invoice_line_id.fal_manual_delivery_fee, None, 1, None, invoice_line_id.invoice_id.partner_id)
                    cur_delivery_fee = invoice_line_id.invoice_id.currency_id
                    delivery_fee_with_vat = cur_delivery_fee.round(taxes_delivery_fee['total_included'])
                    if invoice_line_id.fal_manual_delivery_fee or manual:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = invoice_line_id.price_subtotal_vat / qty + delivery_fee_with_vat / qty
                    else:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = invoice_line_id.price_subtotal_vat / qty + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                else:
                    fapiao_unit_price = unit_price
                totalex = fapiao_unit_price * qty
                tin = []
                for tax_id in invoice_line_id.invoice_line_tax_ids:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if tin:
                    if invoice_line_id.fal_manual_delivery_fee:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = invoice_line_id.price_subtotal_vat + delivery_fee_with_vat
                    else:
                        if not invoice_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = invoice_line_id.price_subtotal_vat + subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee)
                invoice_line_id.fapiao_subtotal_vat = totalex


    fal_manual_delivery_fee = fields.Float('Delivery Fee', digits=dp.get_precision('Account'))
    is_delivery_fees = fields.Boolean('Is Delivery fees')
    fapiao_unit_price_vat = fields.Float(compute=_get_fapiao_unit_price, type='float', string='Fapiao Unit Price VAT Included', help="Fapiao Unit Price", digits=dp.get_precision('Account'), store=True)
    fapiao_subtotal = fields.Float(compute=_get_fapiao_sub_total, type='float', string='Fapiao Subtotal', help="Fapiao Subtotal", digits=dp.get_precision('Account'), store=True)
    fapiao_subtotal_vat = fields.Float(compute=_get_fapiao_sub_total_vat, type='float', string='Fapiao Subtotal VAT Included', help="Fapiao Subtotal VAT Included", digits=dp.get_precision('Account'), store=True)

    @api.model
    def create(self, vals):
        res = super(account_invoice_line, self).create(vals)
        invoice_line_id = self.browse()
        manual = False
        delivery_fee = False
        total_manual_delivery_fee = 0.00
        if invoice_line_id.invoice_id:
            for line in invoice_line_id.invoice_id.invoice_line_ids:
                total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual:
                line_delivery_id.write({'price_unit': total_manual_delivery_fee})
        return res

    @api.multi
    def write(self, vals):
        res = super(account_invoice_line, self).write(vals)
        for invoice_line_id in self:
            manual = False
            delivery_fee = False
            total_manual_delivery_fee = 0.00
            for line in invoice_line_id.invoice_id.invoice_line_ids:
                total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual and not invoice_line_id.is_delivery_fees:
                line_delivery_id.write({'price_unit': total_manual_delivery_fee})
        return res

    @api.multi
    def unlink(self):
        for invoice_line_id in self:
            manual = False
            delivery_fee = False
            total_manual_delivery_fee = 0.00
            for line in invoice_line_id.invoice_id.invoice_line_ids:
                if invoice_line_id.id != line.id:
                    total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual and not invoice_line_id.is_delivery_fees:
                line_delivery_id.write({'price_unit': total_manual_delivery_fee})
        return super(account_invoice_line, self).unlink()
