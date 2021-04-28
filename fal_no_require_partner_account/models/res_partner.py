from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_payable_id = fields.Many2one(
        'account.account', required=False)
    property_account_receivable_id = fields.Many2one(
        'account.account', required=False)
