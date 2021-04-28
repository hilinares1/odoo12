# -*- coding: utf-8 -*-
from odoo import models, api, fields
import datetime
import dateutil.relativedelta


class ProductTemplate(models.Model):
    _name = 'product.template'
    _description = "Product Template"
    _inherit = 'product.template'

    @api.one
    @api.depends('property_cost_method', 'categ_id.property_cost_method')
    def _compute_cost_method(self):
        cost_method = 'average'
        if self.tracking == 'lot':
            cost_method = 'standard'
        self.cost_method = cost_method or self.categ_id.property_cost_method


class StockMove(models.Model):
    _inherit = "stock.move"
    
    @api.multi
    def _action_done(self):
        result = super(StockMove, self)._action_done()
        location_obj = self.env['stock.location']
        parent_id = location_obj.search([('name', '=', 'ATL')])
        stock_location_id = location_obj.search([('name', '=', 'Stock'), ('location_id', '=', parent_id.id)])
        vendor_location_id = location_obj.search([('name', '=', 'Vendors'), ('usage', '=', 'supplier')])
        for record in self:
            product = record.product_id[:1]
            quants = self.env['stock.quant'].search([('product_id', '=', product.id),
                ('location_id', '=', stock_location_id.id)])
            if quants:
                inv_qty = inv_value = value = purchase_qty = purchase_value = 0.0
                for quant in quants:
                    inv_qty += quant.quantity #On hand Qty
                    inv_value = product._sum_remaining_values()[0] #On hand inventory value
                for move in product._sum_remaining_values()[1]:
                    if move.location_id == vendor_location_id and move.location_dest_id == stock_location_id:
                        # purchase_value and purchase_qty base on purchase price and unit
                        purchase_qty += move.purchase_line_id.product_qty
                        purchase_value += move.purchase_line_id.product_qty * move.purchase_line_id.price_unit
                if product.tracking == 'none':
                    if purchase_value > 0 and inv_qty > 0:
                        product.standard_price = float(purchase_value/inv_qty)
                    else:
                        product.standard_price = 0.0
                elif product.tracking == 'serial':
                    if purchase_value > 0 and inv_qty > 0:
                        product.standard_price = float(purchase_value/inv_qty)
                    else:
                        product.standard_price = 0.0
        return result


class Product(models.Model):
    _inherit = "product.product"

    @api.multi
    def update_cost_price(self):
        location_obj = self.env['stock.location']
        parent_id = location_obj.search([('name', '=', 'ATL')])
        stock_location_id = location_obj.search([('name', '=', 'Stock'), ('location_id', '=', parent_id.id)])
        vendor_location_id = location_obj.search([('name', '=', 'Vendors'), ('usage', '=', 'supplier')])
        for record in self.search([]):
            quants = self.env['stock.quant'].search([('product_id', '=', record.id),
                ('location_id', '=', stock_location_id.id)])
            if quants:
                inv_qty = inv_value = purchase_qty = purchase_value = 0.0
                for quant in quants:
                    inv_qty += quant.quantity #On hand Qty
                    inv_value = record._sum_remaining_values()[0] #On hand inventory value
                for move in record._sum_remaining_values()[1]:
                    if move.location_id == vendor_location_id and move.location_dest_id == stock_location_id:
                        # purchase_value and purchase_qty base on purchase price and unit
                        purchase_qty += move.purchase_line_id.product_qty
                        purchase_value += move.purchase_line_id.product_qty * move.purchase_line_id.price_unit
                if record.tracking == 'none':
                    if purchase_value > 0 and inv_qty > 0:
                        record.standard_price = float(purchase_value/inv_qty)
                        # record.standard_price = float(purchase_value/purchase_qty)
                    else:
                        record.standard_price = 0.0
                elif record.tracking == 'serial':
                    if purchase_value > 0 and inv_qty > 0:
                        record.standard_price = float(purchase_value/inv_qty)
                    else:
                        record.standard_price = 0.0
            else:
                record.standard_price = 0.0
