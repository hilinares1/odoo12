from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_moves(self):
        res = super(MrpProduction, self)._generate_moves()
        for production in self:
            points = self.env['quality.point'].search(production._get_quality_point_domain())
            for point in points:
                if point.check_execute_now():
                    for check_id in production.check_ids:
                        production_order_id = self.env['fal.production.order'].search([('name', '=', production.fal_of_number)])
                        if production_order_id:
                            check_id.write({'fal_production_order_id': production_order_id[0].id})
        return res
