from collections import defaultdict
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_quality_checks(self):
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            # If There is no Quality point for this product, but there is Quality point template,
            # Generate it's quality point
            pick_moves[move.picking_id] |= move
            check_quality_points = self.env['quality.point'].sudo().search([
                ('product_tmpl_id', '=', move.product_id.product_tmpl_id.id),
                ('picking_type_id', '=', move.picking_id.picking_type_id.id),
            ], limit=1)
            if not check_quality_points:
                check_quality_points_template = self.env['quality.point'].sudo().search([
                    ('fal_product_category.id', '=', move.product_id.product_tmpl_id.categ_id.id),
                    ('fal_quality_point_template', '=', True),
                    ('picking_type_id.id', '=', move.picking_id.picking_type_id.id)
                ], limit=1)
                if check_quality_points_template:
                    self.env['quality.point'].sudo().create({
                        'title': "QCP " + move.product_tmpl_id.name,
                        'product_id': move.product_id.id,
                        'product_tmpl_id': move.product_tmpl_id.id,
                        'picking_type_id': check_quality_points_template.picking_type_id.id,
                        'measure_frequency_type': check_quality_points_template.measure_frequency_type,
                        'team_id': check_quality_points_template.team_id.id,
                        'fal_test_type_ids': [(6, 0, check_quality_points_template.fal_test_type_ids.ids)],
                    })
        res = super(StockMove, self)._create_quality_checks()

        for mv in self:
            pick_moves[mv.picking_id] |= mv

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
                    ], limit=1)
                    if quality_check_id:
                        quality_check_id.sudo().write({
                            'fal_total_qty_to_check': moves.product_uom_qty,
                            'fal_description': moves.sale_line_id.name,
                        })
                        for fal_test_type in point.fal_test_type_ids:
                            self.env['fal.quality.check'].create({
                                'name': fal_test_type.name,
                                'quality_check_id': quality_check_id.id,
                                'fal_test_type_id': fal_test_type.id,
                                'total_check_ok': quality_check_id.fal_total_qty_to_check,
                                'fal_total_qty_to_check': quality_check_id.fal_total_qty_to_check,
                            })
        return res
