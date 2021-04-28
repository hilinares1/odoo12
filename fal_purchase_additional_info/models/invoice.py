# -*- coding: utf-8 -*-
from odoo import fields, models, api


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.fal_title:
            self.fal_title = self.purchase_id.fal_title
        return super(account_invoice, self).purchase_order_change()
