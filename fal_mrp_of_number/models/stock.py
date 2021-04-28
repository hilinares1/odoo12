from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    @api.depends('sale_line_id')
    def _compute_fal_of_number_id(self):
        for move in self:
            if move.sale_line_id and move.sale_line_id.fal_production_order_id:
                move.fal_of_number_id = move.sale_line_id.fal_production_order_id.id

    fal_of_number_id = fields.Many2one(
        'fal.production.order',
        compute='_compute_fal_of_number_id',
        string='PO Number',
    )


# class StockRule(models.Model):
#     _inherit = 'stock.rule'

#     @api.multi
#     def _run_manufacture(
#             self, product_id, product_qty, product_uom,
#             location_id, name, origin, values):
#         res = super(StockRule, self)._run_manufacture(
#             product_id, product_qty, product_uom, location_id,
#             name, origin, values)
#         stock_move = values.get('move_dest_ids')
#         for move in stock_move:
#             if move.sale_line_id.id:
#                 fal_prod_order = self.env['fal.production.order'].search([('fal_sale_order_line_id','=', move.sale_line_id.id)])
#                 if fal_prod_order:
#                     move.write({'fal_of_number': fal_prod_order.name})
#         return res
