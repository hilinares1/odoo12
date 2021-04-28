# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class FalPutToBox(models.TransientModel):
    _name = "fal.put.to.box"
    _description = "Put to Box"

    box_number = fields.Char(string='Box No.', required=True)
    box_type = fields.Many2one('product.product', string='Type of Box', domain="[('fal_is_package_box', '=', True)]", required=True)
    n_weight = fields.Float(string="Net Weight", digits=dp.get_precision('Product Unit of Measure'), required=True)
    g_weight = fields.Float(string="Gross Weight", digits=dp.get_precision('Product Unit of Measure'), compute='_compute_g_weight')
    delivery_batch_id = fields.Many2one('fal.delivery.batch', string='Delivery Batch ID', default=lambda self: self._get_batch_id())
    delivery_batch_line_wizard_ids = fields.One2many('fal.put.to.box.line.wizard', 'fal_put_to_box_id', string='Delivery Batch Line', default=lambda self: self._get_delivery_batch_line_ids())

    @api.one
    @api.depends('n_weight')
    def _compute_g_weight(self):
        # Gross weight = Net weight + box weight.
        box_weight = 0
        if self.box_type:
            box_weight = self.box_type.weight
        self.g_weight = self.n_weight + box_weight

    @api.model
    def _get_batch_id(self):
        context = dict(self._context or {})
        _logger.info(context.get('active_id', False))
        return context.get('active_id', False)

    @api.model
    def _get_delivery_batch_line_ids(self):
        context = dict(self._context or {})
        batch_id = self.env['fal.delivery.batch'].browse(context.get('active_id', False))
        temp = []
        for batch_line in batch_id.batch_line_ids:
            if batch_line.to_print is not True:
                temp.append((0, 0, {
                    'batch_line_id': batch_line.id,
                    'product_id': batch_line.product_id.id,
                    'name': batch_line.name,
                    'quantity': batch_line.quantity,
                    'balanced_quantity': batch_line.balanced_quantity,
                    'uom_id': batch_line.uom_id.id,
                }))
        return temp

    @api.multi
    def save_to_box(self):
        temp_line = []
        x = 0
        for wizard_line in self.delivery_batch_line_wizard_ids:
            if wizard_line.checkbox is not False:
                x = x + 1
                if wizard_line.allocated_quantity > wizard_line.balanced_quantity:
                    raise UserError(_('You cannot set Allocated Qty more than Balanced Qty.'))
                else:
                    test = self.delivery_batch_id.box_line_ids.filtered(lambda r: r.batch_line_id == wizard_line.batch_line_id and r.box_number == self.box_number and r.box_type == self.box_type)
                    if self.delivery_batch_id.box_line_ids and test:
                        for a in test:
                            a.quantity += wizard_line.allocated_quantity
                    else:
                        temp_line.append((0, 0, {
                            'batch_line_id': wizard_line.batch_line_id.id,
                            'product_id': wizard_line.product_id.id,
                            'name': wizard_line.name,
                            'quantity': wizard_line.allocated_quantity,
                            'uom_id': wizard_line.uom_id.id,
                            'box_number': self.box_number,
                            'box_type': self.box_type.id,
                            'n_weight': self.n_weight,
                            'g_weight': self.g_weight,
                        }))
        if x == 0:
            raise UserError(_('Please select invoice lines and set Allocated Qty.'))
        else:
            self.delivery_batch_id.write({'box_line_ids': temp_line})


class FalPutToBoxLineWizard(models.TransientModel):
    _name = 'fal.put.to.box.line.wizard'
    _description = 'Delivery Batch Line Put to Box'

    checkbox = fields.Boolean(string='Select', default=False)
    fal_put_to_box_id = fields.Many2one('fal.put.to.box', 'Put to Box ID')
    batch_line_id = fields.Many2one('fal.delivery.batch.line', string='Batch Line ID')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    quantity = fields.Float(string='Invoice Qty', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0)
    balanced_quantity = fields.Float(string='Balanced Qty', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0)
    allocated_quantity = fields.Float(string='Allocated Qty', digits=dp.get_precision('Product Unit of Measure'), required=True, default=0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', ondelete='set null', index=True)
