# -*- coding: utf-8 -*-
from odoo import fields, models


class product_category(models.Model):
    _inherit = 'product.category'

    """
    there is no field type on product.category in odoo11
    """
    fal_type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal'),
        ('tool', 'Tool related'),
        ('variant', 'Variant related'),
        ('inner', 'Inner packaging'),
        ('master', 'Master packaging'),
    ], string='Category Type', default='normal')

# end of product_category()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_default_category_id(self):
        res = super(ProductTemplate, self)._get_default_category_id()
        category = self.env['product.category'].browse(res)
        return category and category.fal_type == 'normal' and category.id or False

    categ_id = fields.Many2one(
        domain="[('fal_type','=','normal')]", default=_get_default_category_id)
