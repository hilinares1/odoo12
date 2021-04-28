# -*- coding: utf-8 -*-
from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    fal_warehouse_manager_comment = fields.Text(
        string='Requirer Comment')


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, values, po, partner):
        res = super(StockRule, self)._prepare_purchase_order_line(product_id, product_qty, product_uom, values, po, partner)
        moves = values.get('move_dest_ids')
        if moves:
            for move in moves:
                po.write({'sale_order_line_order_id': move.sale_line_id.order_id.id})
        return res
