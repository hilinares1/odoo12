from odoo import fields, models, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseOrderLine, self).onchange_product_id()
        if self._context.get('from_requisition_process'):
            self.taxes_id = self.order_id.fiscal_position_id.map_tax(
                self.product_id.supplier_taxes_id.filtered(
                    lambda r: r.company_id.id == self.order_id.company_id.id))
        return result