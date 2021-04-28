from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def copy_with_bom(self):
        for product in self:
            duplicate_product_id = product.copy()
            boms = product.bom_ids.filtered(lambda a: a.product_id == product)
            if not boms:
                boms = product.bom_ids
            for bom_id in boms:
                bom_id.copy(default={
                    'product_tmpl_id': duplicate_product_id.product_tmpl_id.id,
                    'product_id': duplicate_product_id.id,
                })
        return duplicate_product_id

    @api.multi
    def action_copy_with_bom(self):
        duplicate_product_id = self.copy_with_bom()
        return {
            'name': 'duplicate_product_id.name',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': duplicate_product_id.id,
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        return super(ProductProduct, self).copy(default=default)
