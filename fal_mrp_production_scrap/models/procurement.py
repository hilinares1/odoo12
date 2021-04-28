from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_fal_mpo_vals(
        self,
        product_id, product_qty, product_uom,
        location_id, name, origin, values,
        bom
    ):
        res = super(StockRule, self)._prepare_fal_mpo_vals(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, bom
        )
        res['scrap_percentage'] = bom.fal_scrap_percentage
        res['qty_to_transfer'] = product_qty
        res['qty_to_produce'] = product_qty / \
            (1 - bom.fal_scrap_percentage / 100.0)
        return res
