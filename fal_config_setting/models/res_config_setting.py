# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Accounting
    module_bank_api = fields.Boolean(
        'Bank Api')
    module_fal_account_ext = fields.Boolean(
        'Account Enhancement')
    module_fal_account_periods_lock = fields.Boolean(
        'Account Period Lock')
    module_fal_analytic_account_ext = fields.Boolean(
        'Analytic Account Enhancement')
    module_fal_crm_multicurrency_group = fields.Boolean(
        'CRM MultiCurrency Group')
    module_fal_customer_statement = fields.Boolean(
        'Customer Statement')
    module_fal_generic_coa = fields.Boolean(
        'Generic Chart Of Account')
    module_fal_generic_coaa = fields.Boolean(
        'Generic Chart Of Analytic Account')
    module_fal_invoice_approval_qualified_partner = fields.Boolean(
        'Invoice Qualified Partner')
    module_fal_invoice_line_account_change = fields.Boolean(
        'Invoice Line Account Change')
    module_fal_invoice_line_analytic_account_change = fields.Boolean(
        'Invoice Line Analytic Account Change')
    module_fal_journal_entries_message = fields.Boolean(
        'Journal Entries Message')
    module_fal_multi_payment_wizard = fields.Boolean(
        'Multi Payment')
    module_fal_multicurrency_group = fields.Boolean(
        'Multi Currency Group')
    module_fal_no_require_partner_account = fields.Boolean(
        'No Require Partner Account')
    module_fal_parent_account = fields.Boolean(
        'Parent Account')
    module_fal_parent_account_hierarchy = fields.Boolean(
        'Parent Account Hierarchy')
    module_fal_payment_bank_provision = fields.Boolean(
        'Payment with Provision')
    module_fal_payment_doku = fields.Boolean(
        'Payment Doku')
    module_fal_product_category_structure = fields.Boolean(
        'Product Category Structure')
    module_fal_project_budget = fields.Boolean(
        'Controlling')
    module_fal_project_dashboard = fields.Boolean(
        'Controlling Dashboard')
    module_fal_tax_comment = fields.Boolean(
        'Tax Comment')
    module_fal_tax_note = fields.Boolean(
        'Tax Note')
    module_fal_timesheet_journal = fields.Boolean(
        'Timesheet Journal')

    # Extra Tools
    module_fal_calendar_meeting_ext = fields.Boolean(
        'Calendar Meeting Enhancement')

    # General
    module_fal_add_message_in_user = fields.Boolean(
        'Add Message In User')
    module_fal_message_body_in_subtype = fields.Boolean(
        'Message Body in Subtype')
    module_fal_block_automatic_email = fields.Boolean(
        'Block Automatic Email')

    # Human Resource
    module_fal_hr_contract_template = fields.Boolean(
        'Employee Contract Template')
    module_fal_hr_ext = fields.Boolean(
        'HR Enhancement')
    module_fal_hr_expense = fields.Boolean(
        'HR Expense')
    module_fal_leave = fields.Boolean(
        'Leave Enhancement')
    module_fal_leave_timesheet = fields.Boolean(
        'Leave Timehseet')
    module_fal_meeting_timesheet = fields.Boolean(
        'Meeting Timesheet')
    module_partner_firstname = fields.Boolean(
        'Partner First Name')
    module_fal_period_lock_hr = fields.Boolean(
        'Period Lock For Employee And Manager')
    module_fal_timesheet_ext = fields.Boolean(
        'Timesheet Extention')
    module_fal_timesheet_invoice_ext = fields.Boolean(
        'Timesheet Invoice')
    module_hr_timesheet_sheet = fields.Boolean(
        'Timesheet Sheet')
    module_fal_timesheet_minimum_hour = fields.Boolean(
        'Timesheet Minimum Hour')
    module_fal_timesheet_template = fields.Boolean(
        'Timesheet Template')
    module_fal_timesheet_sheet_menu = fields.Boolean(
        'Timesheet Sheet Menu')

    # invoicing Management
    module_fal_invoice_milestone = fields.Boolean(
        'Invoice Mailstone')
    module_fal_invoice_sheet_info = fields.Boolean(
        'Invoice Sheet Info')
    module_fal_invoice_additional_info = fields.Boolean(
        'Invoice Additional Info')

    # Localization
    module_fal_l10n_fr = fields.Boolean(
        'French - Accounting')
    module_fal_l10n_id = fields.Boolean(
        'Indonesian - Accounting')
    module_fal_lang_format_ext_fr = fields.Boolean(
        'Language Format France')
    module_indonesian_tax = fields.Boolean(
        'Indonesian Tax')

    # Manufacturing
    module_fal_cost_bom = fields.Boolean(
        'Cost of BOM')
    module_fal_mo_qty = fields.Boolean(
        'Manufacturing Order Quantity')
    module_fal_mrp_costing = fields.Boolean(
        'Manufacturing Costing')
    module_fal_mrp_phantom_routing_operation = fields.Boolean(
        'Phantom Routing Operation')
    module_fal_mrp_production_order = fields.Boolean(
        'Production Order')
    module_fal_mrp_production_scrap = fields.Boolean(
        'Production Scrap')
    module_fal_mrp_sale_link = fields.Boolean(
        'SO Link to Production Order')
    module_fal_mrp_work_route = fields.Boolean(
        'Routing Machine and Working Machine')
    module_fal_mrp_workorder_tracking = fields.Boolean(
        'Manufacturing Time Tracking')
    module_fal_product_copy_bom = fields.Boolean(
        'Product Copy Bom')

    # Partner Management
    module_fal_partner_code = fields.Boolean(
        'Partner Code')
    module_fal_partner_private_address = fields.Boolean(
        'Private Address')
    module_fal_employee_private_contact = fields.Boolean(
        'Employee Private Contract')
    module_fal_partner_short_name = fields.Boolean(
        'Company Shortname')
    module_fal_partner_qualification = fields.Boolean(
        'Partner Qualification')
    module_fal_dynamic_qualification = fields.Boolean(
        'Dynamic Qualification')
    module_fal_partner_user_creation = fields.Boolean(
        'Partner User Creation')

    # Product
    module_fal_generic_product = fields.Boolean(
        'Generic Product')
    module_fal_product_generic = fields.Boolean(
        'Product Enhancement')

    # Project
    module_fal_project_parent_account = fields.Boolean(
        'Project Parent Account')

    # Purchases
    module_fal_product_supplierinfo_discount = fields.Boolean(
        'Product Supplier Info Discount')
    module_fal_procurement_request = fields.Boolean(
        'Purchase Procurement Request')
    module_fal_purchase_additional_info = fields.Boolean(
        'Purchase Additional Info')
    module_fal_purchase_approval_qualified_partner = fields.Boolean(
        'Purchase Approval Qualified Partner')
    module_fal_purchase_discount = fields.Boolean(
        'Purchase Discount')
    module_fal_purchase_downpayment = fields.Boolean(
        'Purchase Downpayment')
    module_fal_purchase_invoice_no_zero_qty = fields.Boolean(
        'Purchase Invoice No Zero Quantity')
    module_fal_purchase_merge = fields.Boolean(
        'Purchase Merge')
    module_fal_purchase_subscription = fields.Boolean(
        'Purchase Subscription')

    # Sales
    module_fal_sale_approval = fields.Boolean(
        'Sale approval')
    fal_is_proposal = fields.Boolean(
        'Via Proposal', help='salesman always go via proposal')
    module_fal_partner_credit_limit = fields.Boolean(
        string="Partner Credit Limit")
    module_fal_minimum_sale = fields.Boolean(
        'Minimum Sale')
    module_fal_sale_approval_qualified_partner = fields.Boolean(
        'Sale Approval Qualified Partner')
    module_fal_sale_additional_info = fields.Boolean(
        'Sale Additional Info')
    module_fal_sale_line_no_onchange = fields.Boolean(
        'Sale line no onchnage')
    module_fal_comment_template = fields.Boolean(
        'Comment Template')

    # Warehouse
    module_fal_stock_adjusment = fields.Boolean(
        'Stock Inventory Valuation')
    module_fal_stock_card = fields.Boolean(
        'Stock Card')

    # Other
    module_web_hierarchy = fields.Boolean(
        'Hierarchial View')

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
