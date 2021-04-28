# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    deduct_downpayment_purchase = fields.Boolean(string='Deduct DownPayment',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Encoding help. Deduct Downpayment')

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self).\
            _prepare_invoice_line_from_po_line(line)
        if self.deduct_downpayment_purchase:
            if line.fal_is_downpayment and line.qty_invoiced != 0:
                res['quantity'] = -1.0
        return res
