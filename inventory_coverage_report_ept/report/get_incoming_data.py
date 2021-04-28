# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import date_utils


class ReportInventoryQuantity(models.Model):
    _name = 'get.incoming.data'
    _auto = False
    _description = 'Get Incoming Data Report'

    incoming_date = fields.Date(string='Incoming Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', readonly=True)
    period_id = fields.Many2one('requisition.period.ept', string='Period', readonly=True)
    incoming = fields.Float('Incoming Qunatity', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'get_incoming_data')
        query = """
                CREATE or REPLACE VIEW get_incoming_data AS (
                 Select
                    incoming_date, 
                    product_id, 
                    warehouse_id, 
                    period.id as period_id, 
                    sum(product_uom_qty) as incoming 
                from 
                (
                    select
                            move.date_expected::date as incoming_date,
                            move.product_id,
                            ware.id as warehouse_id, 
                            move.product_uom_qty
                    from
                         stock_move move
                            Inner Join stock_location source on source.id = move.location_id
                            Inner Join stock_location dest on dest.id = move.location_dest_id
                            Inner Join stock_warehouse ware on dest.parent_path ~~ concat('%/',ware.view_location_id,'/%')
                    Where source.usage = 'supplier' and dest.usage = 'internal' and move.state not in ('draft','done','cancel')
                )T
                    Inner Join requisition_period_ept period on period.date_start <= T.incoming_date and period.date_stop >= T.incoming_date
                group by incoming_date, product_id, warehouse_id, period.id
                    );
            """
        self.env.cr.execute(query)
