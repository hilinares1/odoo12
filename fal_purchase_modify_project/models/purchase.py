# -*- coding: utf-8 -*-
from odoo import models, api


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_project_modify(self):
        context = {'default_project_id': self.order_line and self.order_line[0].account_analytic_id.id}
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.purchase.project.modify.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

# end of purchase_order()
