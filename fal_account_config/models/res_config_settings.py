# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Setup
    module_fal_account_invoice_sequence = fields.Boolean(
        'Invoice Draft Sequence')
    module_fal_generic_coa = fields.Boolean(
        'Generic Chart Of Account')

# Accounting
    module_account_bank_statement_reconciliation = fields.Boolean(
        'Account Bank Statements Menu')
    module_fal_account_bank_statement_reconciliation_ext = fields.Boolean(
        'ACC: Bank Statement Reconciliation Ext')
    module_fal_account_cancel_ext = fields.Boolean(
        'ACC-02_Account Cancel Ext')
    module_fal_bank_statement_sequence = fields.Boolean(
        'Bank Statement Sequence')
    module_fal_account_ext = fields.Boolean(
        'Account Enhancement')
    module_fal_analytic_account_ext = fields.Boolean(
        'Analytic Account Enhancement')
    module_fal_analytic_account_tag = fields.Boolean(
        'Analytic Account Tag')
    module_fal_parent_account = fields.Boolean(
        'Parent Account')
    module_fal_parent_account_hierarchy = fields.Boolean(
        'Parent Account Hierarchy')
    module_fal_journal_entries_message = fields.Boolean(
        'Journal Entries Message')
    module_fal_multi_payment_wizard = fields.Boolean(
        'Multi Payment')
    module_fal_no_require_partner_account = fields.Boolean(
        'No Require Partner Account')
    module_fal_account_periods_lock = fields.Boolean(
        'Account Period Lock')
    module_fal_customer_statement = fields.Boolean(
        'Customer Statement')
    module_bank_api = fields.Boolean(
        'Bank Api')
    module_fal_generic_coaa = fields.Boolean(
        'Generic Chart Of Analytic Account')
    module_fal_invoice_line_account_change = fields.Boolean(
        'Invoice Line Account Change')
    module_fal_invoice_approval_qualified_partner = fields.Boolean(
        'Invoice Qualified Partner')
    module_fal_tax_note = fields.Boolean(
        'Tax Note')
    module_fal_invoice_line_analytic_account_change = fields.Boolean(
        'Invoice Line Analytic Account Change')
    module_fal_multicurrency_group = fields.Boolean(
        'Multi Currency Group')
    module_fal_payment_bank_provision = fields.Boolean(
        'Payment with Provision')

# Accounting Asset
    module_fal_asset_ext = fields.Boolean(
        'Account Asset Extension')

# invoicing Management
    module_fal_invoice_additional_info = fields.Boolean(
        'Invoice Additional Info')
    module_fal_invoice_print_attachment = fields.Boolean(
        'Invoice Print Attachment')

# Localization
    module_fal_lang_format_ext_fr = fields.Boolean(
        'Language Format France')
    module_indonesian_tax = fields.Boolean(
        'Indonesian Tax')

# New Account Module
    module_fal_consolidation_multi_currency = fields.Boolean(
        'Consolidation IFRS')
    module_fal_contract_conditions_invoice = fields.Boolean(
        'Contract Conditions Invoice')
    module_fal_contract_conditions_voucher = fields.Boolean(
        'Contract Conditions Voucher')
    module_fal_financial_report = fields.Boolean(
        'Falinwa Report Financial')
    module_fal_invoice_delivery_fee = fields.Boolean(
        'Invoice Delivery Fee')
    module_fal_invoice_line = fields.Boolean(
        'Customer Invoice and Vendor Bills Relation')
    module_fal_invoice_reminder = fields.Boolean(
        'REP-03_Invoice Reminder')
    module_fal_l10n_cn = fields.Boolean(
        'China - Accounting')
    module_fal_l10n_fec = fields.Boolean(
        'Falinwa FEC')
    module_fal_l10n_cn_fapiao_enterprise = fields.Boolean(
        'China - Fapiao for Enterprise')
    module_fal_l10n_cn_payroll = fields.Boolean(
        'HRD-08_Payroll China Falinwa')
    module_fal_l10n_cn_report = fields.Boolean(
        'ACC: Falinwa China Report')
    module_fal_project_in_account_partner_product = fields.Boolean(
        'Analytic Account in Invoice Partner Product')
    module_fal_project_in_partner_product = fields.Boolean(
        'Analytic Account in Partner And Product')
    module_fal_project_in_purchase_partner_product = fields.Boolean(
        'Analytic Account in Purchase Partner Product')
    module_fal_project_in_sale_partner_product = fields.Boolean(
        'Analytic Account in Sale Partner Product')
    module_fal_tax_product_categ = fields.Boolean(
        'Tax Product Category')
    module_l10n_cn_fapiao = fields.Boolean(
        'Chinese Fapiao Management')
    module_terms_conditions = fields.Boolean(
        'Documents - Terms and Conditions')
    module_fal_consolidation_nonintra = fields.Boolean(
        'Consolidation Non Intra')
    module_fal_account_deferred_cost = fields.Boolean(
        'Deferred Cost')
    module_fal_partner_netting = fields.Boolean(
        'Falinwa Partner Netting')
    module_fal_account_report_groupby = fields.Boolean(
        'Falinwa Report Financial Groupby')
    module_fal_account_deferred_cost = fields.Boolean(
        'Deferred Cost')
    module_fal_account_provision = fields.Boolean(
        'Provision')

    @api.onchange('group_analytic_accounting')
    def _onchange_group_analytic_accounting(self):
        if self.group_analytic_accounting:
            self.group_analytic_accounting = True
