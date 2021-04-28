from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    fal_on_hands_qty = fields.Float(
        related='product_id.qty_available', string='Qty on Hand')
