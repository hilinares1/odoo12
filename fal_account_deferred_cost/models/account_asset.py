from odoo import models, fields


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    type = fields.Selection([
        ('sale', 'Sale: Revenue Recognition'),
        ('purchase', 'Purchase: Asset'),
        ('cost', 'Deferred Cost')],
        required=True, index=True, default='purchase')
