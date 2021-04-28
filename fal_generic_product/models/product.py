from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_generic_product = fields.Boolean(string='Generic Product', default=False)
