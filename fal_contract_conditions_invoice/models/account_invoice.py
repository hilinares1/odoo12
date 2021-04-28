from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('contract_condition_id')
    def onchange_contract_condition_id(self):
        if self.contract_condition_id:
            self.comment = self.contract_condition_id.content

    contract_condition_id = fields.Many2one(
        'contract.condition',
        string='Contract Condition'
    )
