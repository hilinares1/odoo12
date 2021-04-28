from odoo import models, api

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_sale_order_line_data(self, line, company, sale_id):
        res = super(PurchaseOrder, self)._prepare_sale_order_line_data(line, company, sale_id)
        res['product_no_variant_attribute_value_ids'] = [(6, 0, line.product_no_variant_attribute_value_ids.ids)]
        return res
