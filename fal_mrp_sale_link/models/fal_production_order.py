from odoo import models, fields, api


class FalProductionOrder(models.Model):
    _inherit = 'fal.production.order'

    fal_sale_order_id = fields.Many2one(
        'sale.order', string='Sale Order')
    fal_sale_order_line_id = fields.Many2one(
        'sale.order.line', string='Sale Order Line')
