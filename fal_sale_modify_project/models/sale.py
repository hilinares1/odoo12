# -*- coding: utf-8 -*-
from odoo import models, api


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_project_modify(self):
        context = {'default_project_id': self.analytic_account_id.id}

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.modify.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
