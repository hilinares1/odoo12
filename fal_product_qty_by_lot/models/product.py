 # -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fal_lot_number_ids = fields.Many2many(
        'stock.production.lot', string='Lot / SN',
        readonly=True, compute='_compute_lot_number'
    )

    def _compute_lot_number(self):
        for product in self:
            lot = self.env['stock.production.lot'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('fal_state', '!=', 'close')
            ])
            product.fal_lot_number_ids = [(6, 0, lot.ids)]
