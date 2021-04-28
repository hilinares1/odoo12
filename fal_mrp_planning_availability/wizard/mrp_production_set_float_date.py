from odoo import fields, models
# from openerp.tools.translate import _


class mrp_production_set_float_date(models.TransientModel):
    _name = "mrp.production.set.float.date.wizard"

    float_date = fields.Date('Float Date', required=1)

    def set_float_date(self):
        production_id = self.env['mrp.production'].browse(self.env.context.get('active_ids', False))
        production_id.write({'fal_floating_production_date': self.float_date, })
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
