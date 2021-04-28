# -*- coding: utf-8 -*-
from odoo import models, fields


class FalWarningMessage(models.Model):
    _name = 'fal.warning.message'

    name = fields.Char(string='Title')
    description = fields.Text(string='Warning Message')
    sequence = fields.Integer(string='Sequence')
    product_categ_ids = fields.Many2many(
        'product.category', 'fal_warning_message_prodcat_rel', 'warning_id',
        'categ_id', string='Finished Product Category')
    cons_product_categ_ids = fields.Many2many(
        'product.category', 'fal_warning_message_cons_prodcat_rel',
        'warning_id', 'categ_id', string='To Consume Product Category')
    routing_ids = fields.Many2many(
        'mrp.routing', 'fal_warning_message_routing_rel', 'warning_id',
        'routing_id', string='Routing')
    workcenter_ids = fields.Many2many(
        'mrp.workcenter', 'fal_warning_message_workcenter_rel',
        'warning_id', 'workcenter_id', string='Work Center')
    product_ids = fields.Many2many(
        'product.product', 'fal_warning_message_product_rel', 'warning_id',
        'product_id', string='Finished Products')
    cons_product_ids = fields.Many2many(
        'product.product', 'fal_warning_message_cons_product_rel',
        'warning_id', 'product_id', string='To Consume Products')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    fal_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_product_rel',
        'product_id', 'warning_id', string='Warning Messages for Products')
    fal_cons_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_cons_product_rel',
        'product_id', 'warning_id', string='Warning Messages for Consume Products')


class MrpWorkCenter(models.Model):
    _inherit = 'mrp.workcenter'

    fal_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_workcenter_rel',
        'workcenter_id', 'warning_id',
        string='Warning Messages for Workcenter')


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    fal_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_routing_rel',
        'routing_id', 'warning_id', string='Warning Messages for Routing')


class ProdCat(models.Model):
    _inherit = 'product.category'

    fal_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_prodcat_rel', 'categ_id',
        'warning_id', string='Warning Messages for Product Category')
    fal_cons_warning_message_ids = fields.Many2many(
        'fal.warning.message', 'fal_warning_message_cons_prodcat_rel',
        'categ_id', 'warning_id',
        string='Warning Messages for Consume Product Category')
