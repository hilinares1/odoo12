from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _get_quality_check_values(self, quality_point):
        res = super(MrpProduction, self)._get_quality_check_values(quality_point)
        res['fal_total_qty_to_check'] = self.product_qty
        return res

    @api.multi
    def _generate_moves(self):
        for production in self:
            # If There is no Quality point for this product, but there is Quality point template,
            # Generate it's quality point
            check_quality_points = self.env['quality.point'].sudo().search([
                ('product_tmpl_id', '=', production.product_id.product_tmpl_id.id),
                ('picking_type_id', '=', production.picking_type_id.id),
            ], limit=1)
            if not check_quality_points:
                check_quality_points_template = self.env['quality.point'].sudo().search([
                    ('fal_product_category', '=', production.product_id.product_tmpl_id.categ_id.id),
                    ('fal_quality_point_template', '=', True),
                    ('picking_type_id', '=', production.picking_type_id.id)], limit=1)

                if check_quality_points_template:
                    self.env['quality.point'].sudo().create({
                        'title': "QCP " + production.product_tmpl_id.name,
                        'product_id': production.product_id.id,
                        'product_tmpl_id': production.product_tmpl_id.id,
                        'picking_type_id': check_quality_points_template.picking_type_id.id,
                        'measure_frequency_type': check_quality_points_template.measure_frequency_type,
                        'team_id': check_quality_points_template.team_id.id,
                        'fal_test_type_ids': [(6, 0, check_quality_points_template.fal_test_type_ids.ids)],
                    })
        res = super(MrpProduction, self)._generate_moves()
            # Then generate the Fal Quality Check on the quality check, based on fal test type on the quality point
        for quality_check in self.check_ids.filtered(lambda x: x.quality_state == 'none'):
            for fal_test_type in quality_check.point_id.fal_test_type_ids:
                self.env['fal.quality.check'].create({
                    'name': fal_test_type.name,
                    'quality_check_id': quality_check.id,
                    'fal_test_type_id': fal_test_type.id,
                    'total_check_ok': quality_check.fal_total_qty_to_check,
                    'fal_total_qty_to_check': quality_check.fal_total_qty_to_check,
                })
        return res
