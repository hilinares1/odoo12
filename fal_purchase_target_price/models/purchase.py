from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    total_supplier_target_price = fields.Float(string='Total Supplier Target Price', compute='_compute_total_supplier_target_price', digits=dp.get_precision('Account'), store=True)
    total_gross_margin = fields.Float(string='Total Gross Margin', compute='_compute_total_gross_margin', digits=dp.get_precision('Account'))
    total_markup = fields.Float(string='Total Mark-up %', compute='_compute_total_markup', store=True)

    @api.depends('order_line.supplier_target_unit_price')
    def _compute_total_supplier_target_price(self):
        for order in self:
            val = 0.00
            for order_line in order.order_line:
                val += order_line.supplier_target_unit_price
            order.total_supplier_target_price = val

    @api.depends('order_line.gross_margin')
    def _compute_total_gross_margin(self):
        for order in self:
            val = 0.00
            for order_line in order.order_line:
                val += order_line.gross_margin
            order.total_gross_margin = val

    @api.depends('order_line.mark_up')
    def _compute_total_markup(self):
        for order in self:
            val = 0.00
            for order_line in order.order_line:
                val += order_line.mark_up
            order.total_markup = val


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier_target_unit_price = fields.Float(string='Supplier Target Unit Price (Customer Currency)', digits=dp.get_precision('Product Price'))
    supplier_target_subtotal = fields.Float(string='Supplier Target Subtotal (Customer Currency)', compute='_compute_supplier_target_subtotal', digits=dp.get_precision('Account'), store=True)
    gross_margin = fields.Float(string='Gross Margin', compute='_compute_gross_margin', digits=dp.get_precision('Account'), store=True)
    mark_up = fields.Float(string='Mark-up %', compute='_compute_markup', store=True)

    @api.depends('product_qty', 'supplier_target_unit_price')
    def _compute_supplier_target_subtotal(self):
        for line in self:
            line.supplier_target_subtotal = line.product_qty * line.supplier_target_unit_price

    @api.depends('price_unit', 'supplier_target_unit_price')
    def _compute_gross_margin(self):
        for line in self:
            line.gross_margin = line.price_unit - line.supplier_target_unit_price

    @api.depends('gross_margin', 'supplier_target_unit_price')
    def _compute_markup(self):
        for line in self:
            markup = 0.00
            if line.gross_margin and line.supplier_target_unit_price:
                markup = float(line.gross_margin / line.supplier_target_unit_price) * 100
                line.mark_up = markup
