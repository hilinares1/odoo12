# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import date_utils


class GetProductStock(models.Model):
    _name = 'get.product.stock'
    _auto = False
    _description = 'Get Product Stock Warehouse Wise'

    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', readonly=True)
    qty_available = fields.Float(string='Available QTY', Readonly=True)
    qty_reserved = fields.Float(string='Reserved QTY', Readonly=True)
    net_on_hand = fields.Float(string='Net On Hand QTY', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'get_product_stock')
        query = """
                    CREATE or REPLACE VIEW get_product_stock AS (
                    Select 
                    *,
                    qty_available - qty_reserved as net_on_hand
                    from 
                    (
                    Select 
                    quant.product_id as product_id,
                    ware.id as warehouse_id,
                    sum(quant.quantity) as qty_available,
                    sum(quant.reserved_quantity) as qty_reserved
                    From 
                    stock_quant quant 
                    Inner Join stock_location loc on loc.id = quant.location_id
                    Left Join stock_warehouse ware on loc.parent_path ~~ concat('%/', ware.view_location_id,'/%')
                    Where loc.usage = 'internal'
                    group by quant.product_id, ware.id
                    ) T
                    );    
            """
        self._cr.execute(query)
