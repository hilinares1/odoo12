from odoo import fields, models, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    fal_taxes_id = fields.Many2many(
        'account.tax', 'product_category_taxes_rel',
        'category_id', 'tax_id', string='Customer Taxes',
        domain=[('type_tax_use', '=', 'sale')])
    fal_supplier_taxes_id = fields.Many2many(
        'account.tax', 'product_category_supplier_taxes_id',
        'category_id', 'tax_id', string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase')])

    @api.multi
    def write(self, values):
        res = super(ProductCategory, self).write(values)
        for categ in self:
            product_ids = self.env['product.template'].search([('categ_id', '=', categ.id)])
            if values.get('fal_supplier_taxes_id', False):
                product_ids.write({'supplier_taxes_id': values.get('fal_supplier_taxes_id')})
            if values.get('fal_taxes_id', False):
                product_ids.write({'taxes_id': values.get('fal_taxes_id')})
        return res
