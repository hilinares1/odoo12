# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# invoicing Management
    module_fal_invoice_milestone = fields.Boolean(
        'Invoice Milestone')
    module_fal_invoice_sheet_info = fields.Boolean(
        'Invoice Sheet Info')

# Sales
    module_fal_sale_additional_info = fields.Boolean(
        'Sale Additional Info')
    module_fal_sale_line_no_onchange = fields.Boolean(
        'Sale Line No Onchnage')
    module_fal_sale_approval = fields.Boolean(
        'Sale approval')
    module_fal_partner_credit_limit = fields.Boolean(
        string="Partner Credit Limit")
    module_fal_credit_limit_formula = fields.Boolean(
        string="Credit Limit AR Formula", help="Based on SO/PO amount")
    module_fal_minimum_sale = fields.Boolean(
        'Minimum Sale')
    module_fal_sale_approval_qualified_partner = fields.Boolean(
        'Sale Approval Qualified Partner')
    fal_is_proposal = fields.Boolean(
        'Via Proposal', help='salesman always go via proposal')
# New Sale
    module_fal_contract_conditions_sale = fields.Boolean(
        'Contract Conditions Sale')
    module_fal_group_by_commercial = fields.Boolean(
        'Group By Commercial')
    module_fal_sale_modify_project = fields.Boolean(
        'Sale Modify Analytic Account')
    module_fal_sale_order_sheet_invoice = fields.Boolean(
        'Sale Order Sheet on Invoice')
    module_fal_sale_product_selector = fields.Boolean(
        'Sale Product Attribute')
    module_fal_sale_sequence = fields.Boolean(
        'Sale Sequence')
    module_fal_sale_subscription_ext = fields.Boolean(
        'Sales Subscription: title, attachment, extend')
    module_fal_sale_target_price = fields.Boolean(
        'Sale Target Price')
    module_fal_sale_production_of_number = fields.Boolean(
        'Sale Production Order Number')
    module_fal_sale_calculator = fields.Boolean(
        'Sale Calculator')
    module_fal_quotation_revision = fields.Boolean(
        'Sale Quotation Revision')

    @api.onchange('fal_is_proposal')
    def _onchange_fal_is_proposal(self):
        if self.fal_is_proposal:
            self.module_fal_partner_credit_limit = False
            self.module_fal_minimum_sale = False
            self.module_fal_sale_approval_qualified_partner = False

    @api.model
    def get_values(self):
        res = super(FalResConfigSettings, self).get_values()
        ctx = dict(self._context)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        fal_is_proposal = ICPSudo.get_param(
            'fal_config_setting.fal_is_proposal')
        res.update(
            fal_is_proposal=fal_is_proposal,
        )
        ctx.update({'fal_is_proposal': True})
        return res

    @api.multi
    def set_values(self):
        res = super(FalResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "fal_config_setting.fal_is_proposal",
            self.fal_is_proposal)
        return res
