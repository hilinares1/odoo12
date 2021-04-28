from odoo import fields, models, api


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.onchange('contract_condition_id')
    def onchange_contract_condition_id(self):
        if self.contract_condition_id:
            self.narration = self.contract_condition_id.content

    contract_condition_id = fields.Many2one(
        'contract.condition',
        string='Contract Condition'
    )
