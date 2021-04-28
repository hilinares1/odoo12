# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp


class ProductLotDiscard(models.TransientModel):
    _name = "product.lot.discard"
    _description = "Product LoT Discard"

    @api.multi
    def go_to_scrap(self):
        self.ensure_one()
        return {
            'name': _('Scrap'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'res_id': self.env.context.get('scrap_id'),
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

# End of ProcurementRequestWizard()
