from collections import defaultdict
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_quality_checks(self):
        res = super(StockMove, self)._create_quality_checks()
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            pick_moves[move.picking_id] |= move

        for picking, moves in pick_moves.items():
            quality_points = self.env['quality.point'].sudo().search([
                ('picking_type_id', '=', picking.picking_type_id.id),
                '|', ('product_id', 'in', moves.mapped('product_id').ids),
                '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
            for point in quality_points:
                if point.check_execute_now():
                    quality_check_id = self.env['quality.check'].sudo().search([
                        ('picking_id', '=', picking.id),
                        ('point_id', '=', point.id),
                        ('product_id', '=', point.product_id.id)
                    ])
                    production_order_id = self.env['fal.production.order'].search([('name', '=', moves.fal_of_number)])
                    quality_check_id.sudo().write({
                        'fal_production_order_id': production_order_id and production_order_id[0].id,
                    })
        return res
