from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Product attribute values that do not create variants')


class product_selector(models.TransientModel):
    _inherit = 'product.selector'

    @api.onchange('product_selector_line_ids')
    def onchange_product_selector_line_ids(self):
        res = super(product_selector, self).onchange_product_selector_line_ids()
        if self.env.context.get('model') == 'purchase.order':
            new_product_ids = []
            for item in self.product_ids.ids:
                if self.env['product.product'].browse(item).purchase_ok:
                    new_product_ids.append(item)
            self.product_ids = [(6, 0, new_product_ids)]
        return res
