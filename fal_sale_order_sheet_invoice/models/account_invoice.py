# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_ids = fields.Many2many(
        'sale.order', string='Sales',
        compute='_fal_get_so_lines', readonly=True,
        help="This is the list of sale that related to this Invoice")

    @api.depends(
        'invoice_line_ids', 'invoice_line_ids.sale_line_ids',
        'invoice_line_ids.sale_line_ids.order_id')
    def _fal_get_so_lines(self):
        order_ids = []
        for line in self:
            for order_line in line.invoice_line_ids:
                if order_line.sale_line_ids:
                    for sale_order_line in order_line.sale_line_ids:
                        if sale_order_line.order_id.id not in order_ids:
                            order_ids.append(sale_order_line.order_id.id)
                # serach on origin if no sale order line in invoice line
                else:
                    order = self.env['sale.order'].search([('name', '=', order_line.origin)])
                    if order:
                        if order.id not in order_ids:
                            order_ids.append(order.id)
        line.sale_ids = [(6, 0, order_ids)]
