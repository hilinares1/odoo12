# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.onchange('contract_condition_id')
    def onchange_contract_condition_id(self):
        if self.contract_condition_id:
            self.notes = self.contract_condition_id.content

    contract_condition_id = fields.Many2one(
        'contract.condition',
        string='Contract Condition'
    )
