from odoo import models, fields, api, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def _create_checks(self):
        for workorder in self:
            check_quality_points = self.env['quality.point'].sudo().search([('product_tmpl_id.id', '=', workorder.product_id.product_tmpl_id.id)], limit=1)
            if not check_quality_points:
                check_quality_points_template = self.env['quality.point'].sudo().search([('fal_product_category.id', '=', workorder.product_id.product_tmpl_id.categ_id.id), ('fal_quality_point_template', '=', True), ('operation_id.id', '=', workorder.operation_id.id), ('picking_type_id.id', '=', workorder.production_id.picking_type_id.id)], limit=1)

                if check_quality_points_template:
                    self.env['quality.point'].sudo().create({
                        'title': "QCP "+workorder.product_id.product_tmpl_id.name,
                        'product_id': workorder.product_id.id,
                        'product_tmpl_id': workorder.product_id.product_tmpl_id.id,
                        'picking_type_id': check_quality_points_template.picking_type_id.id,
                        'measure_frequency_type': check_quality_points_template.measure_frequency_type,
                        'team_id': check_quality_points_template.team_id.id,
                        'fal_test_type_ids': [(6, 0, check_quality_points_template.fal_test_type_ids.ids)],
                        'operation_id': check_quality_points_template.operation_id.id,
                        'company_id': check_quality_points_template.company_id.id
                    })
        res = super(MrpWorkorder, self)._create_checks()
        production = workorder.production_id
        points = self.env['quality.point'].search([('operation_id', '=', workorder.operation_id.id),
                                                       ('picking_type_id', '=', production.picking_type_id.id),
                                                       '|', ('product_id', '=', production.product_id.id),
                                                       '&', ('product_id', '=', False), ('product_tmpl_id', '=', production.product_id.product_tmpl_id.id)])
        for point in points:
            if point.check_execute_now():
                quality_check_id = self.env['quality.check'].search([
                    ('workorder_id', '=', workorder.id),
                    ('point_id', '=', point.id),
                    ('product_id', '=', production.product_id.id),
                ], limit=1)
                if quality_check_id:
                    quality_check_id.write({
                        'production_id': production.id,
                        'fal_total_qty_to_check': production.product_qty,
                    })
                    for fal_test_type in point.fal_test_type_ids:
                        self.env['fal.quality.check'].create({
                            'name': fal_test_type.name,
                            'checklist': False,
                            'quality_check_id': quality_check_id.id,
                            'fal_parent_test_type_id': fal_test_type.parent_id.id or False,
                            'fal_test_type_id': fal_test_type.id,
                            'total_check_ok': quality_check_id.fal_total_qty_to_check,
                            'fal_total_qty_to_check': quality_check_id.fal_total_qty_to_check,
                        })
        return res
