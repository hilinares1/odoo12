# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Purchases
    module_fal_product_supplierinfo_discount = fields.Boolean(
        'Product Supplier Info Discount')
    module_fal_purchase_additional_info = fields.Boolean(
        'Purchase Additional Info')
    module_fal_purchase_merge = fields.Boolean(
        'Purchase Merge')
    module_fal_procurement_request = fields.Boolean(
        'Purchase Procurement Request')
    module_fal_procurement_email = fields.Boolean(
        'Procurement Request by Email')
    module_fal_purchase_approval_qualified_partner = fields.Boolean(
        'Purchase Approval Qualified Partner')
    module_fal_purchase_downpayment = fields.Boolean(
        'Purchase Downpayment')
    module_fal_purchase_invoice_no_zero_qty = fields.Boolean(
        'Purchase Invoice No Zero Quantity')
    module_fal_purchase_subscription = fields.Boolean(
        'Purchase Subscription')
    module_fal_purchase_discount = fields.Boolean(
        'Purchase Discount')
    module_fal_purchase_approval = fields.Boolean(
        'Purchase Approval')
    fal_purc_is_proposal = fields.Boolean(
        'Via Proposal', help='purchase user always go via proposal')

# New Purchase
    module_fal_contract_conditions_purchase = fields.Boolean(
        'Contract Conditions Purchase')
    module_fal_product_category_vendor = fields.Boolean(
        'Product Category Vendor')
    module_fal_purchase_modify_project = fields.Boolean(
        'Purchase Modify Analytic Account')
    module_fal_purchase_order_sheet_invoice = fields.Boolean(
        'Purchase Order Sheet on Invoice')
    module_fal_purchase_product_selector = fields.Boolean(
        'Purchase Product Attribute')
    module_fal_purchase_production_of_number = fields.Boolean(
        'Purchase Production Order Number')
    module_fal_purchase_sequence = fields.Boolean(
        'Purchase Sequence')
    module_fal_purchase_target_price = fields.Boolean(
        'Purchase Target Price')
    module_fal_srm = fields.Boolean(
        'Supplier Relationship Management')

# Config for Procurement Email

    fal_procurement_alias_prefix = fields.Char('Default Alias Name for Procurement')

    module_fal_last_purchase_price = fields.Boolean(
        'Costing method: Last Purchase Price')

    @api.onchange('po_order_approval')
    def _onchange_po_order_approval(self):
        if self.po_order_approval:
            self.fal_purc_is_proposal = False

    @api.onchange('fal_purc_is_proposal')
    def _onchange_fal_purc_is_proposal(self):
        if self.fal_purc_is_proposal:
            self.po_order_approval = False

    @api.model
    def get_values(self):
        res = super(FalResConfigSettings, self).get_values()
        ctx = dict(self._context)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        fal_purc_is_proposal = ICPSudo.get_param(
            'fal_config_setting.fal_purc_is_proposal')
        res.update(
            fal_purc_is_proposal=fal_purc_is_proposal,
        )
        ctx.update({'fal_purc_is_proposal': True})
        
        return res

    @api.multi
    def set_values(self):
        res = super(FalResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "fal_config_setting.fal_purc_is_proposal",
            self.fal_purc_is_proposal)
        return res
