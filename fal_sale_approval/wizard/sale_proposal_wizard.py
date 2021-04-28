
# -*- coding: utf-8 -*-
from odoo import models, api, fields


class sale_propose_wizard(models.TransientModel):
    _name = "fal.sale.proposal.wizard"
    _description = "Sale Approval Wizard"

    sale_order_id = fields.Many2one(
        "sale.order", default=lambda self: self._context.get('active_id'))

    @api.multi
    def action_propose(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        sale = self.env['sale.order'].browse(active_id)
        sale.action_wait()

    @api.multi
    def manager_confirm(self):
        self.sale_order_id.action_confirm()
