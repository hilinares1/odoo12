from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    @api.depends('is_delivery_fees', 'fal_manual_delivery_fee', 'discount', 'price_unit', 'product_uom_qty', 'tax_id', 'order_id')
    def _get_fapiao_unit_price(self):
        for order_line_id in self:
            soline = order_line_id.name
            if soline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = order_line_id.price_subtotal_vat
                subtotal_delivery_fee = 0.00
                unit_price = order_line_id.price_unit * (1 - (order_line_id.discount or 0.0) / 100.0)
                qty = order_line_id.product_uom_qty
                tin = []
                manual = False
                for tax_id in order_line_id.tax_id:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if order_line_id.order_id:
                    for order_line_id_in_order in order_line_id.order_id.order_line:
                        if order_line_id_in_order.is_delivery_fees:
                            subtotal_delivery_fee += order_line_id_in_order.price_subtotal_vat
                        total += order_line_id_in_order.price_subtotal_vat
                        if order_line_id_in_order.fal_manual_delivery_fee:
                            manual = True
                    if order_line_id.fal_manual_delivery_fee or manual:
                        if not order_line_id.is_delivery_fees:
                            if subtotal:
                                if tin:
                                    fapiao_unit_price = unit_price + order_line_id.fal_manual_delivery_fee / qty
                                else:
                                    taxes_delivery_fee = order_line_id.tax_id.compute_all(order_line_id.fal_manual_delivery_fee, None, 1, None, order_line_id.order_id.partner_id)
                                    cur_delivery_fee = order_line_id.order_id.pricelist_id.currency_id
                                    delivery_fee_with_vat = cur_delivery_fee.round(taxes_delivery_fee['total_included'])
                                    fapiao_unit_price = order_line_id.price_subtotal_vat / qty + delivery_fee_with_vat / qty
                    else:
                        if not order_line_id.is_delivery_fees:
                            if subtotal:
                                if tin:
                                    fapiao_unit_price = unit_price + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                                else:
                                    fapiao_unit_price = order_line_id.price_subtotal_vat / qty + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)

                else:
                    fapiao_unit_price = unit_price
                order_line_id.fapiao_unit_price_vat = fapiao_unit_price

    @api.multi
    @api.depends('is_delivery_fees', 'fal_manual_delivery_fee', 'discount', 'price_unit', 'product_uom_qty', 'tax_id', 'order_id')
    def _get_fapiao_sub_total(self):
        for order_line_id in self:
            soline = order_line_id.name
            if soline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = order_line_id.price_subtotal
                subtotal_delivery_fee = 0.00
                unit_price = order_line_id.price_unit * (1 - (order_line_id.discount or 0.0) / 100.0)
                qty = order_line_id.product_uom_qty
                manual = False
                if order_line_id.order_id:
                    for order_line_id_in_order in order_line_id.order_id.order_line:
                        if order_line_id_in_order.is_delivery_fees:
                            subtotal_delivery_fee += order_line_id_in_order.price_subtotal
                        total += order_line_id_in_order.price_subtotal
                        if order_line_id_in_order.fal_manual_delivery_fee:
                            manual = True
                    if order_line_id.fal_manual_delivery_fee or manual:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = unit_price + order_line_id.fal_manual_delivery_fee / qty
                    else:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = unit_price + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                else:
                    fapiao_unit_price = unit_price
                totalex = fapiao_unit_price * qty
                tin = []
                for tax_id in order_line_id.tax_id:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if tin:
                    if order_line_id.fal_manual_delivery_fee or manual:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = order_line_id.price_subtotal + order_line_id.fal_manual_delivery_fee
                    else:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = order_line_id.price_subtotal + subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee)
                order_line_id.fapiao_subtotal = totalex

    @api.multi
    @api.depends('is_delivery_fees', 'fal_manual_delivery_fee', 'discount', 'price_unit', 'product_uom_qty', 'tax_id', 'order_id')
    def _get_fapiao_sub_total_vat(self):
        for order_line_id in self:
            soline = order_line_id.name
            if soline:
                fapiao_unit_price = 0.00
                total = 0.00
                subtotal = order_line_id.price_subtotal_vat
                subtotal_delivery_fee = 0.00
                unit_price = order_line_id.price_unit * (1 - (order_line_id.discount or 0.0) / 100.0)
                qty = order_line_id.product_uom_qty
                manual = False
                if order_line_id.order_id:
                    for order_line_id_in_order in order_line_id.order_id.order_line:
                        if order_line_id_in_order.is_delivery_fees:
                            subtotal_delivery_fee += order_line_id_in_order.price_subtotal_vat
                        total += order_line_id_in_order.price_subtotal_vat
                        if order_line_id_in_order.fal_manual_delivery_fee:
                            manual = True
                    taxes_delivery_fee = order_line_id.tax_id.compute_all(order_line_id.fal_manual_delivery_fee, None, 1, None, order_line_id.order_id.partner_id)
                    cur_delivery_fee = order_line_id.order_id.pricelist_id.currency_id
                    delivery_fee_with_vat = cur_delivery_fee.round(taxes_delivery_fee['total_included'])
                    if order_line_id.fal_manual_delivery_fee or manual:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = order_line_id.price_subtotal_vat / qty + delivery_fee_with_vat / qty
                    else:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                fapiao_unit_price = order_line_id.price_subtotal_vat / qty + (subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee) / qty)
                else:
                    fapiao_unit_price = unit_price
                totalex = fapiao_unit_price * qty
                tin = []
                for tax_id in order_line_id.tax_id:
                    if tax_id.price_include:
                        tin.append(tax_id)
                if tin:
                    if order_line_id.fal_manual_delivery_fee or manual:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = order_line_id.price_subtotal_vat + delivery_fee_with_vat
                    else:
                        if not order_line_id.is_delivery_fees:
                            if subtotal and total:
                                totalex = order_line_id.price_subtotal_vat + subtotal_delivery_fee * subtotal / (total - subtotal_delivery_fee)
                order_line_id.fapiao_subtotal_vat = totalex

    fal_manual_delivery_fee = fields.Float('Delivery Fee', digits=dp.get_precision('Account'))
    is_delivery_fees = fields.Boolean('Is Delivery fees')
    fapiao_unit_price_vat = fields.Float(compute=_get_fapiao_unit_price, type='float', string='Fapiao Unit Price VAT Included', help="Fapiao Unit Price", digits=dp.get_precision('Account'), store=True)
    fapiao_subtotal = fields.Float(compute=_get_fapiao_sub_total, type='float', string='Fapiao Subtotal', help="Fapiao Subtotal", digits=dp.get_precision('Account'), store=True)
    fapiao_subtotal_vat = fields.Float(compute=_get_fapiao_sub_total_vat, type='float', string='Fapiao Subtotal VAT Included', help="Fapiao Subtotal VAT Included", digits=dp.get_precision('Account'), store=True)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['is_delivery_fees'] = self.is_delivery_fees
        res['fal_manual_delivery_fee'] = self.fal_manual_delivery_fee
        if self.is_delivery_fees:
            res['sequence'] = 999
        return res

    @api.model
    def create(self, values):
        res = super(SaleOrderLine, self).create(values)
        for order_line_id in res:
            manual = False
            delivery_fee = False
            total_manual_delivery_fee = 0.00
            for line in order_line_id.order_id.order_line:
                total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual:
                line_delivery_id.write(
                    {'price_unit': total_manual_delivery_fee})
        return res

    @api.multi
    def write(self, values):
        res = super(SaleOrderLine, self).write(values)
        for order_line_id in self:
            manual = False
            delivery_fee = False
            total_manual_delivery_fee = 0.00
            for line in order_line_id.order_id.order_line:
                total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual and not order_line_id.is_delivery_fees:
                line_delivery_id.write(
                    {'price_unit': total_manual_delivery_fee})
        return res

    @api.multi
    def unlink(self):
        for order_line_id in self:
            manual = False
            delivery_fee = False
            total_manual_delivery_fee = 0.00
            for line in order_line_id.order_id.order_line:
                if order_line_id.id != line.id:
                    total_manual_delivery_fee += line.fal_manual_delivery_fee
                if line.fal_manual_delivery_fee:
                    manual = True
                if line.is_delivery_fees:
                    delivery_fee = True
                    line_delivery_id = line
            if delivery_fee and manual and not order_line_id.is_delivery_fees:
                line_delivery_id.write(
                    {'price_unit': total_manual_delivery_fee})
        return super(SaleOrderLine, self).unlink()


class StockMove(models.Model):
    _inherit = 'stock.move'

    fal_manual_delivery_fee = fields.Float('Delivery Fee', digits=dp.get_precision('Account'))
