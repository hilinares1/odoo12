from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['final_quotation_number'] = self.quotation_number or self.name
        if self.company_id.fal_company_late_payment_statement:
            res['fal_use_late_payment_statement'] = True
        if self.client_order_ref:
            res['fal_client_order_ref'] = self.client_order_ref
        if self.quotation_number:
            res['fal_quotation_number'] = self.quotation_number
            res['final_quotation_number'] = self.quotation_number or self.name
        return res

# merge from falinwa_field_ext
