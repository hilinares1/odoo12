# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    fal_config_ids = fields.One2many('fal.product.attribute.config', 'attribute_id', 'Config', copy=False)
    attribute_image = fields.Binary(string="Attribute Image", attachment=True)


class ProductAttributeConfig(models.Model):
    _name = "fal.product.attribute.config"
    _order = 'attribute_id, sequence, id'
    _description = 'Attribute Config'

    sequence = fields.Integer(string='Sequence', help="Determine the display order", index=True)
    attribute_id = fields.Many2one('product.attribute', string='Attribute')
    attribute_value_id = fields.Many2many('product.attribute.value', string='Value', required=True)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    fal_config_ids = fields.One2many('fal.product.attribute.value.config', 'value_id', string='Config', copy=False)
    attribute_value_image = fields.Binary(string="Attribute Value Image", attachment=True)


class ProductAttributeValueConfig(models.Model):
    _name = "fal.product.attribute.value.config"
    _order = 'value_id, sequence, id'
    _description = 'Attribute Config'

    sequence = fields.Integer(string='Sequence', help="Determine the display order", index=True)
    value_id = fields.Many2one('product.attribute.value', string='Attribute Value')
    attribute_value_id = fields.Many2many('product.attribute.value', string='Value')


class ProductAttributeAddButton(models.Model):
    _inherit = 'product.product'

    fal_product_selector_selected = fields.Boolean('Selected', default=False, help="Select product to add to sale order line")
