from odoo import models, fields, api, _


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.multi
    def _create_checks(self):
        res = super(MrpWorkorder, self)._create_checks()
        for workorder in self:
            production = workorder.production_id
            points = self.env['quality.point'].search([
                ('operation_id', '=', workorder.operation_id.id),
                ('picking_type_id', '=', production.picking_type_id.id),
                '|', ('product_id', '=', production.product_id.id),
                '&', ('product_id', '=', False),
                ('product_tmpl_id', '=', production.product_id.product_tmpl_id.id)
            ])
            for point in points:
                if point.check_execute_now():
                    quality_check_id = self.env['quality.check'].search([
                        ('workorder_id', '=', workorder.id),
                        ('point_id', '=', point.id),
                        ('product_id', '=', production.product_id.id),
                    ], limit=1)
                    if quality_check_id:
                        quality_check_id.sudo().write({
                            'fal_production_order_id': production.fal_prod_order_id.id,
                        })
        return res
