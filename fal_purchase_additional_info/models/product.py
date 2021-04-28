from odoo import models, api, fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # new field to get product_name from supplier_info
    fal_supplier_info_product_name = fields.Char('Product Name from Vendors', compute='_compute_product_code')

    @api.one
    def _compute_product_code(self):
        res = super(ProductProduct, self)._compute_product_code()
        for supplier_info in self.seller_ids:
            if supplier_info.name.id == self._context.get('partner_id'):
                self.fal_supplier_info_product_name = supplier_info.product_name
        return res
