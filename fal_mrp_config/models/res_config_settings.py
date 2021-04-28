# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


# Manufacturing
    module_fal_cost_bom = fields.Boolean(
        'Cost of BOM')
    module_fal_mrp_costing = fields.Boolean(
        'Manufacturing Costing')
    module_fal_mrp_production_scrap = fields.Boolean(
        'Production Scrap')
    module_fal_mo_qty = fields.Boolean(
        'Manufacturing Order Quantity')
    module_fal_mrp_sale_link = fields.Boolean(
        'SO Link to Production Order')
    module_fal_product_copy_bom = fields.Boolean(
        'Product Copy Bom')
    module_fal_mrp_phantom_routing_operation = fields.Boolean(
        'Phantom Routing Operation')
    module_fal_mrp_production_order = fields.Boolean(
        'Production Order')
    module_fal_mrp_work_route = fields.Boolean(
        'Routing Machine and Working Machine')
    module_fal_mrp_workorder_tracking = fields.Boolean(
        'Manufacturing Time Tracking')
# New MRP
    module_fal_finished_product_sequence = fields.Boolean(
        'Finished Product Sequence')
    module_fal_mrp_ext = fields.Boolean(
        'MRP Enhancement')
    module_fal_mrp_of_number = fields.Boolean(
        'MRP Stock PO Number')
    module_fal_mrp_planning_availability = fields.Boolean(
        'MRP Planning Availability')
    module_fal_mrp_product_selector = fields.Boolean(
        'MRP Product Attribute')
    module_fal_mrp_project = fields.Boolean(
        'MRP Project')
    module_fal_mrp_warning_message = fields.Boolean(
        'Warning Message Management for MRP')
    module_fal_production_order_product_selector = fields.Boolean(
        'Production Order Product Attribute')
    module_fal_quality = fields.Boolean(
        'Fal Quality')
    module_fal_quality_alert_5m = fields.Boolean(
        'Fal Quality Alert 5M')
    module_fal_quality_alert_5y = fields.Boolean(
        'Fal Quality Alert 5Y')
    module_fal_quality_ext = fields.Boolean(
        'Quality Extends Module')
    module_fal_quality_print_sticker = fields.Boolean(
        'Quality Print Sticker')
    module_fal_quality_production_order = fields.Boolean(
        'Fal Quality Production Order')
    module_fal_repair_product_selector = fields.Boolean(
        'Repair Order Product Attribute')
    module_fal_routing_ext = fields.Boolean(
        'Fal Routing Extension')
