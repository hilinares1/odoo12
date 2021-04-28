from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(
            self, product_id, product_qty, product_uom,
            location_id, name, origin, values):
        res = super(StockRule, self)._run_manufacture(
            product_id, product_qty, product_uom, location_id,
            name, origin, values)
        order_line_id = values.get('move_dest_ids', False) \
            and values.get('move_dest_ids').sale_line_id.id
        MPO = self.env['fal.production.order'].search(
            [('fal_sale_order_line_id', '=', order_line_id)])
        if MPO:
            for MPO_id in MPO:
                MPO_id.fal_sale_order_line_id.write({'fal_production_order_id': MPO_id.id})
        return res

    # write sale_line_id or sale_order_id in production order
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
        order_line_id = values.get('move_dest_ids', False) \
            and values.get('move_dest_ids').sale_line_id.id
        order_id = values.get('move_dest_ids', False) \
            and values.get('move_dest_ids').sale_line_id.order_id.id
        res['fal_sale_order_id'] = order_id
        res['fal_sale_order_line_id'] = order_line_id
        return res
