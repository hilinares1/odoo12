# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Orderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    logic = fields.Selection([
        ('max', 'Order to Max'),
        # ('price', 'Best price (not yet active!)'),
        ('fix', 'Order Quantity')],
        string='Reordering Mode', required=True)

    product_order_label_qty = fields.Float(compute='_compute_product_order_qty', string='Re-ordering Quantity', store=False)

    @api.multi
    def _compute_product_order_qty(self):
        for orderpoint in self:
            orderpoint.product_order_label_qty = orderpoint.product_max_qty - orderpoint.product_min_qty
