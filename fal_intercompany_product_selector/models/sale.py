from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, purchase_id, company):
        res = super(SaleOrder, self)._prepare_purchase_order_line_data(so_line, date_order, purchase_id, company)
        res['product_no_variant_attribute_value_ids'] = [(6, 0, so_line.product_no_variant_attribute_value_ids.ids)]
        return res
