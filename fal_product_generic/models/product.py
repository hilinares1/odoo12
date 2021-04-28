from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fal_stock_product = fields.Boolean(
        string='Is Stock Product',
        default=False)
    property_account_income_id = fields.Many2one(copy=True)
    property_account_expense_id = fields.Many2one(copy=True)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super(ProductProduct, self).copy(default=default)
