# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        old_description = self.name
        res = super(SaleOrderLine, self).product_id_change()
        if old_description:
            self.name = old_description
        return res
