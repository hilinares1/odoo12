# -*- coding: utf-8 -*-
from odoo import api, models


class sale_order(models.Model):

    _inherit = "sale.order"

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, purchase_id, company):
        res = super(sale_order, self)._prepare_purchase_order_line_data(so_line, date_order, purchase_id, company)
        if not so_line.product_id.is_generic_product:
            res.update({'name': so_line.product_id.display_name})
        return res
