# -*- coding: utf-8 -*-
from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class FalDeliveryBatch(models.Model):
    _inherit = "fal.delivery.batch"

    total_value_words_cn = fields.Text(string='Total Value in Words 中文')
    port_of_loading_cn = fields.Char(string='Port Of Loading 中文', related='port_of_loading.port_name_cn')
    port_of_discharge_cn = fields.Char(string='Port Of Discharge 中文', related='port_of_discharge.port_name_cn')
    fapiao_amount_total = fields.Float(string='Fapiao Total', store=True, readonly=True, compute='_amount_all')

    @api.depends('batch_line_ids.fapiao_subtotal_vat')
    def _amount_all(self):
        res = super(FalDeliveryBatch, self)._amount_all()
        for batch in self:
            total = 0.0
            for line in batch.batch_line_ids:
                if not line.to_print:
                    total += line.fapiao_subtotal_vat
            batch.fapiao_amount_total = total
        return res


class FalDeliveryBatchLine(models.Model):
    _inherit = "fal.delivery.batch.line"

    fapiao_price_unit = fields.Float(string='Fapiao Unit Price VAT Included', required=True, digits=dp.get_precision('Product Price'))
    fapiao_subtotal_vat = fields.Float(compute='_compute_fapiao_subtotal', string='Fapiao Subtotal VAT Included', help="Fapiao Subtotal VAT Included", digits=dp.get_precision('Account'), store=True)

    @api.depends('quantity', 'fapiao_price_unit', 'invoice_line_id')
    def _compute_fapiao_subtotal(self):
        for line in self:
            line.fapiao_subtotal_vat = line.quantity * line.fapiao_price_unit


class FalPortType(models.Model):
    _inherit = 'fal.port.type'

    port_name_cn = fields.Char(string='Port Name 中文')
