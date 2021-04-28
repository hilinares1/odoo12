# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return

        if self.product_id.seller_ids:
            return super(PurchaseOrderLine, self)._suggest_quantity()
        else:
            if not self.product_id:
                return

            seller_min_qty = self.product_id.categ_id.fal_seller_ids\
                .filtered(lambda r: r.name == self.order_id.partner_id)\
                .sorted(key=lambda r: r.min_qty)
            if seller_min_qty:
                self.product_qty = seller_min_qty[0].min_qty or 1.0
                self.product_uom = seller_min_qty[0].product_uom
            else:
                self.product_qty = 1.0
