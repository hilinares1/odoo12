from odoo import models, api, fields


class PurchaseOrdre(models.Model):
    _inherit = 'purchase.order'

    fal_invoice_paid = fields.Boolean(
        string="Paid All Invoice ?",
        compute='get_status_from_line',
        store=True,)

    @api.one
    @api.depends('state', 'invoice_status')
    def get_status_from_line(self):
        if self.state in ['purchase', 'done'] and self.invoice_status == 'invoiced':
            invoice_ids = self.order_line.mapped(
                'invoice_lines').mapped(
                'invoice_id').filtered(
                lambda r: r.type in ['in_invoice', 'in_refund'])
            all_invoice_paid = True
            for invoice in invoice_ids:
                if invoice.state != 'paid':
                    all_invoice_paid = False
            self.update(
                {'fal_invoice_paid': all_invoice_paid})
        else:
            self.update(
                {'fal_invoice_paid': False})
