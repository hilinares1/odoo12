from odoo import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    fal_same_value = fields.Boolean(compute='fal_update_invisible')

    def update_to_consume(self):
        self.unit_factor = self.product_uom_qty

    @api.depends('product_uom_qty', 'unit_factor')
    def fal_update_invisible(self):
        for item in self:
            if item.product_uom_qty == item.unit_factor:
                item.fal_same_value = True
