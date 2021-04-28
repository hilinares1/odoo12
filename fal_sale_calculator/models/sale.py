from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fal_is_product_selector = fields.Boolean(string='Is Product Selector', readonly=False, default=False)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        price_unit = self.price_unit
        result = super(SaleOrderLine, self).product_id_change()
        if self.fal_is_product_selector:
            self.price_unit = price_unit
        return result

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        price_unit = self.price_unit
        result = super(SaleOrderLine, self).product_uom_change()
        if self.fal_is_product_selector:
            self.price_unit = price_unit
        return result
