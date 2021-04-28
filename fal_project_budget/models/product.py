# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    fal_margin_percentage = fields.Float('Expected Margin')
