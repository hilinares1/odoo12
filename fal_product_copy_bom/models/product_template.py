from odoo import models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def copy_with_bom(self):
        for product_template in self:
            duplicate_product_template_id = product_template.copy()
            for bom_id in product_template.bom_ids:
                bom_id.copy(default={
                    'product_tmpl_id': duplicate_product_template_id.id,
                })
        return duplicate_product_template_id

    @api.multi
    def action_copy_with_bom(self):
        duplicate_product_template_id = self.copy_with_bom()
        return {
            'name': 'duplicate_product_template_id.name',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': duplicate_product_template_id.id,
            'res_model': 'product.template',
            'type': 'ir.actions.act_window',
        }
