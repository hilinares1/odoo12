# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    purchase_ids = fields.Many2many(
        'purchase.order', string='Purchases', compute='_fal_get_po_line',
        readonly=True, help="Purchase Orders That related to Invoice")

    @api.depends(
        'invoice_line_ids', 'invoice_line_ids.purchase_line_id',
        'invoice_line_ids.purchase_line_id.order_id')
    def _fal_get_po_line(self):
        order_ids = []
        for line in self:
            for order_line in line.invoice_line_ids:
                for purchase_order_line in order_line.purchase_line_id:
                    if purchase_order_line.order_id.id not in order_ids:
                        order_ids.append(purchase_order_line.order_id.id)
        line.purchase_ids = [(6, 0, order_ids)]
