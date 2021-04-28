
# -*- coding: utf-8 -*-
from odoo import models, api, fields


class sale_propose_wizard(models.TransientModel):
    _inherit = "fal.sale.proposal.wizard"

    is_below_minimum = fields.Boolean("Below Minimum Price", compute="_is_below_minimum")
    is_above_maximum = fields.Boolean("Above Maximum Price", compute="_is_above_maximum")

    @api.multi
    @api.depends('sale_order_id')
    def _is_above_maximum(self):
        for order_line in self.sale_order_id.order_line:
            if order_line.is_above_maximum:
                self.is_above_maximum = True

    @api.multi
    @api.depends('sale_order_id')
    def _is_below_minimum(self):
        for order_line in self.sale_order_id.order_line:
            if order_line.is_below_minimum:
                self.is_below_minimum = True
