from odoo import fields, models
from odoo.addons import decimal_precision as dp


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    # Salesman
    fal_salesman_max_reduce = fields.Float(
        'Salesman Max Reduce', default=0.0,
        help="Maximum Price reduction in percentage for Salesman. Salesman cannot sell this product with price under (Computed Pricelist Price - this percentage)")

    fal_salesman_max_increase = fields.Float(
        'Salesman Max Increase', default=0.0,
        help="Maximum Price increment in percentage for Salesman. Salesman cannot sell this product with price above (Computed Pricelist Price + this percentage)")
