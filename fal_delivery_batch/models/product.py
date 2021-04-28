from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    fal_is_package_box = fields.Boolean(string="Is Package Box", default=False)


class ProductCategory(models.Model):
    _inherit = "product.category"

    fal_description_packing_list = fields.Char(string="Description Packing List")
