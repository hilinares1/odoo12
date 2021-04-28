# -*- coding: utf-8 -*-

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        # remove line with zero qty
        prev_lines = self.invoice_line_ids
        res = super(AccountInvoice, self).purchase_order_change()
        self.invoice_line_ids -= (
            self.invoice_line_ids.filtered(lambda x: x.quantity == 0) -
            prev_lines
        )
        return res
