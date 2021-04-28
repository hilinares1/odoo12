# -*- coding: utf-8 -*-
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class FalRegisterDeliveryBatch(models.TransientModel):
    _inherit = "fal.register.delivery.batch"

    @api.model
    def _get_invoice_line_ids(self):
        temp = super(FalRegisterDeliveryBatch, self)._get_invoice_line_ids()
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        temp = []
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            for invoice_line in invoice_id.invoice_line_ids:
                temp.append((0, 0, {
                    'invoice_line_id': invoice_line.id,
                    'product_id': invoice_line.product_id.id,
                    'name': invoice_line.name,
                    'quantity': invoice_line.quantity,
                    'uom_id': invoice_line.uom_id.id,
                    'price_unit': invoice_line.price_unit,
                    'fapiao_price_unit': invoice_line.fapiao_unit_price_vat,
                }))
        return temp
