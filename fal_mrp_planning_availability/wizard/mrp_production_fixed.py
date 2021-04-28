from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class mrp_production_fixed(models.TransientModel):
    _name = "mrp.production.fixed.wizard"

    def production_fixed(self):
        self.env['mrp.production'].browse(self.env.context.get('active_ids', False))._production_fixed()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
