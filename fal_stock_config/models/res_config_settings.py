# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

#Setup
    module_fal_adjustment_inventory_ext = fields.Boolean(
        'Adjustment Inventory filter')
    
#Accounting
    module_fal_product_category_structure = fields.Boolean(
        'Product Category Structure')

# Product
    module_fal_generic_product = fields.Boolean(
        'Generic Product')
    module_fal_product_generic = fields.Boolean(
        'Product Enhancement')

# Warehouse
    module_fal_stock_adjusment = fields.Boolean(
        'Stock Inventory Valuation')
    module_fal_stock_card = fields.Boolean(
        'Stock Card')

# New Stock
    module_fal_chinese_delivery_batch = fields.Boolean(
        'China delivery batches')
    module_fal_delivery_batch = fields.Boolean(
        'Delivery Batch')
    module_fal_inventory_ext = fields.Boolean(
        'Inventory Extends')
    module_fal_print_sticker = fields.Boolean(
        'Print Sticker')
    module_fal_product_attribute = fields.Boolean(
        'Print Sticker')
    module_fal_product_qty_by_lot = fields.Boolean(
        'Advanced LoT/SN Management')
    module_fal_product_size_detail = fields.Boolean(
        'Product Detailed Specification')
    module_fal_serial_number_sticker = fields.Boolean(
        'Serial Number Sticker')
    module_fal_stock_menu = fields.Boolean(
        'Picking Menu Extension')
    module_fix_quantity_reordering_rules = fields.Boolean(
        'Quantity Reordering Rule')
    module_product_label_report = fields.Boolean(
        'Product Label')
    