# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class product_selector(models.TransientModel):
    _name = 'product.selector'

    product_selector_line_ids = fields.One2many('product.selector.line', 'product_selector_id', string="Attribute(s)")
    product_id = fields.Many2one("product.product", "Product")
    product_ids = fields.Many2many('product.product', string="Product Options")
    fal_available_value_ids = fields.Many2many('product.attribute.value', string="Available Attribute Value(s)")

    @api.onchange('product_selector_line_ids')
    def onchange_product_selector_line_ids(self):
        product_ids = []
        attribute_value_ids = []
        for product_selector_line_id in self.product_selector_line_ids:
            if product_selector_line_id.value_id and product_selector_line_id.atribute_id.create_variant == 'always':
                query = """SELECT product_product_id
                            FROM product_attribute_value_product_product_rel
                            WHERE product_attribute_value_id = %s
                            """
                if product_ids:
                    query += """AND product_product_id IN %s
                                """
                    self.env.cr.execute(query, (product_selector_line_id.value_id.id, tuple(product_ids)))
                else:
                    self.env.cr.execute(query, [product_selector_line_id.value_id.id])
                product_ids = []
                for val in self.env.cr.dictfetchall():
                    product_ids.append(val['product_product_id'])
            attribute_value_ids.append(product_selector_line_id.value_id.id)
        if self.env.context.get('model') == 'sale.order':
            new_product_ids = []
            for item in product_ids:
                if self.env['product.product'].browse(item).sale_ok:
                    new_product_ids.append(item)
            product_ids = new_product_ids
        self.fal_available_value_ids = attribute_value_ids
        self.product_ids = [(6, 0, product_ids)]
        if len(self.product_ids) == 1:
            self.product_id = self.product_ids


class product_selector_line(models.TransientModel):
    _name = 'product.selector.line'

    product_selector_id = fields.Many2one('product.selector', string="Selector")
    atribute_id = fields.Many2one('product.attribute', string="Attribute")
    value_id = fields.Many2one('product.attribute.value', string="Value", required=True)
    fal_available_value_ids = fields.Many2many('product.attribute.value', related='product_selector_id.fal_available_value_ids', string='Attribute Value(s)')

    @api.multi
    @api.onchange('fal_available_value_ids', 'atribute_id')
    def fal_available_value_ids_change(self):
        atribute_value_ids = []
        active_attribute_ids = []
        for fal_available_value_id in self.fal_available_value_ids:
            atribute_value_ids.append(fal_available_value_id.id)
            active_attribute_ids.append(fal_available_value_id.attribute_id.id)
        available_attribute_ids = self.attribute_requirement_check(atribute_value_ids)
        available_attribute_value_ids = self.attribute_value_requirement_check(atribute_value_ids)
        return {
            'domain': {
                'atribute_id': [('id', 'in', available_attribute_ids)],
                'value_id': [('id', 'in', available_attribute_value_ids)]
            }}

    def attribute_requirement_check(self, atribute_value_ids):
        result = self.env['product.attribute'].search([('fal_config_ids', '=', False)]).ids
        attributes = self.env['product.attribute'].search([('fal_config_ids', '!=', False)])
        for attribute in attributes:
            all_requirement_fulfilled = True
            for config in attribute.fal_config_ids:
                is_found_in_or = False
                for value in config.attribute_value_id:
                    if value.id in atribute_value_ids:
                        is_found_in_or = True
                if not is_found_in_or:
                    all_requirement_fulfilled = False
            if all_requirement_fulfilled:
                result.append(attribute.id)
        return result

    def attribute_value_requirement_check(self, atribute_value_ids):
        result = self.env['product.attribute.value'].search([('fal_config_ids', '=', False)]).ids
        attribute_values = self.env['product.attribute.value'].search([('fal_config_ids', '!=', False)])
        for attribute_value in attribute_values:
            all_requirement_fulfilled = True
            for config in attribute_value.fal_config_ids:
                is_found_in_or = False
                for value in config.attribute_value_id:
                    if value.id in atribute_value_ids:
                        is_found_in_or = True
                if not is_found_in_or:
                    all_requirement_fulfilled = False
            if all_requirement_fulfilled:
                result.append(attribute_value.id)
        return result
