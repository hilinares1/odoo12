
from odoo import models, api


class multi_check_stock_mrp_wizard(models.TransientModel):
    _name = "multi.check.stock.mrp.wizard"

    @api.multi
    def action_check(self):
        context = dict(self._context)
        if context.get('active_ids', False):
            mrp_obj = self.env['mrp.production']
            for mrp in mrp_obj.browse(context.get('active_ids', False)):
                if mrp.state == 'confirmed':
                    mrp.action_assign()
