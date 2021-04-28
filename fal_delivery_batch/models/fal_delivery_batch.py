# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class FalDeliveryBatch(models.Model):
    _name = "fal.delivery.batch"
    _description = "Delivery Batch"
    _rec_name = 'number'

    number = fields.Char(string='SCDB Number', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    total_value_words = fields.Text(string='Total Value in Words')
    contract_number = fields.Char(string='Contract Number')
    invoice_number = fields.Char(string='Invoice Number')
    create_date = fields.Datetime(string="Create On", default=lambda self: datetime.datetime.now())
    port_of_loading = fields.Many2one('fal.port.type', string='Port Of Loading', default=lambda self: self._get_default_port_loading())
    port_of_discharge = fields.Many2one('fal.port.type', string='Port Of Discharge', default=lambda self: self._get_default_port_discharge())
    batch_line_ids = fields.One2many('fal.delivery.batch.line', 'batch_id', string='Invoice Line')
    box_line_ids = fields.One2many('fal.delivery.box.line', 'batch_id', string='Box Line')
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one('res.currency', string='Currency')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    packaging_and_shipping = fields.Char(string='Packing and shipping Marks', default='Wooden Box')
    carrier = fields.Char(string='Carrier', default='By Air')

    @api.depends('batch_line_ids.subtotal_vat')
    def _amount_all(self):
        for batch in self:
            total = 0.0
            for line in batch.batch_line_ids:
                if not line.to_print:
                    total += line.subtotal_vat
            batch.amount_total = total

    def _get_default_port_loading(self):
        port_object = self.env['fal.port.type']
        default_port_loading = port_object.search([('is_default_loading', '=', True)], limit=1).id or False
        return default_port_loading

    def _get_default_port_discharge(self):
        port_object = self.env['fal.port.type']
        default_port_discharge = port_object.search([('is_default_discharge', '=', True)], limit=1).id or False
        return default_port_discharge


class FalDeliveryBatchLine(models.Model):
    _name = "fal.delivery.batch.line"
    _description = "Invoices Line"
    _rec_name = 'name'

    batch_id = fields.Many2one('fal.delivery.batch', string='Batch Reference')
    invoice_line_id = fields.Many2one('account.invoice.line', string='Invoice Line')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1)
    balanced_quantity = fields.Float(string='Balanced Quantity', digits=dp.get_precision('Product Unit of Measure'), compute='_compute_balance_qty')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', ondelete='set null', index=True)
    price_unit = fields.Float(string='Unit Price VAT Included', required=True, digits=dp.get_precision('Product Price'))
    subtotal_vat =fields.Float(compute='_compute_subtotal', string='Subtotal VAT Included', help="Subtotal VAT Included", digits=dp.get_precision('Account'), store=True)
    to_print = fields.Boolean(string="Do not Show", default=False)
    box_line_ids = fields.One2many('fal.delivery.box.line', 'batch_line_id', string='Box Line')
    currency_id = fields.Many2one('res.currency', string='Currency', related="batch_id.currency_id")

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal_vat = line.quantity * line.price_unit

    @api.multi
    def _compute_balance_qty(self):
        for line in self:
            balance_qty = 0
            for box_line in line.box_line_ids:
                balance_qty += box_line.quantity
            line.balanced_quantity = line.quantity - balance_qty

    @api.onchange('price_unit')
    def onchange_price_unit(self):
        for line in self:
            line.subtotal_vat = line.quantity * line.price_unit


class FalDeliveryBoxLine(models.Model):
    _name = "fal.delivery.box.line"
    _description = "Delivery Box Line"
    _rec_name = 'product_id'
    _order = 'box_number'

    batch_id = fields.Many2one('fal.delivery.batch', string='Batch Reference')
    box_number = fields.Char(string='Box No.')
    box_type = fields.Many2one('product.product', string='Box Type', domain="[('fal_is_package_box', '=', True)]")
    box_length = fields.Float(string='Length', related='box_type.fal_length')
    box_width = fields.Float(string='Width', related='box_type.fal_width')
    box_height = fields.Float(string='Height', related='box_type.fal_height')
    box_total = fields.Integer(string='Total Box', compute='_compute_total_box', store=True)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description', required=True)
    quantity = fields.Float(string='Allocated Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', ondelete='set null', index=True)
    n_weight = fields.Float(string="Net Weight", digits=dp.get_precision('Product Unit of Measure'))
    g_weight = fields.Float(string="Gross Weight", digits=dp.get_precision('Product Unit of Measure'))
    batch_line_id = fields.Many2one('fal.delivery.batch.line', string='Batch Line')

    @api.one
    @api.depends('batch_id.box_line_ids')
    def _compute_total_box(self):
        for box in self.batch_id.box_line_ids:
            box.box_total = len(box.batch_id.box_line_ids.filtered(lambda r: r.box_number == box.box_number))


class FalPortType(models.Model):
    _name = 'fal.port.type'
    _description = 'Port Type'
    _rec_name = 'port_name'

    port_name = fields.Char(string='Port Name')
    is_default_loading = fields.Boolean(string='Default Port of Loading')
    is_default_discharge = fields.Boolean(string='Default Port of Discharge')
