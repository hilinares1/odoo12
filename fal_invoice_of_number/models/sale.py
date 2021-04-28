from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if self.fal_production_order_id:
            res['fal_of_number'] = self.fal_production_order_id.name
            res['fal_of_number_id'] = self.fal_production_order_id.id
        return res
