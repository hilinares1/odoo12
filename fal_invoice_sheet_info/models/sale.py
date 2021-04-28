from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_invoice_paid = fields.Boolean(
        string="Paid All Invoice ?",
        compute='get_status_from_line',
        store=True,)

    @api.one
    @api.depends('state', 'invoice_status')
    def get_status_from_line(self):
        # If order type == sale order
        # If sale order invoice status is invoiced and all the invoice related to this sale order is on status paid. Then True, else False
        if self.state in ['sale', 'done'] and self.invoice_status in ['invoiced', 'upselling']:
            invoice_ids = self.order_line.mapped(
                'invoice_lines').mapped(
                'invoice_id').filtered(
                lambda r: r.type in ['out_invoice', 'out_refund'])
            all_invoice_paid = True
            for invoice in invoice_ids:
                if invoice.state != 'paid':
                    all_invoice_paid = False
            self.update(
                {'fal_invoice_paid': all_invoice_paid})
        else:
            self.update(
                {'fal_invoice_paid': False})
