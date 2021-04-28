from odoo import api, fields, models, _


class AccountAnalytic(models.Model):
    _inherit = "account.analytic.account"

    company_id = fields.Many2one(default=False)
    description = fields.Text('Description')

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id(self):
        # No need to check company compatibility
        return True
