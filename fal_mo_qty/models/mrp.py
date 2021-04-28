# -*- coding: utf-8 -*-
from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends(
        'product_qty',
        'qty_produced',
    )
    def _compute_fal_product_produced_qty(self):
        self.fal_product_tobe_produce = self.product_qty - self.qty_produced

    fal_product_tobe_produce = fields.Float(
        string='Remaining Qty',
        compute=_compute_fal_product_produced_qty,
    )

# end of mrp_production()
