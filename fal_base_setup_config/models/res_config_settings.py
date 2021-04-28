# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# General
    module_create_and_edit_many2one = fields.Boolean(
        'Create and Edit Many2one Feature')
    module_fal_add_message_in_user = fields.Boolean(
        'Add Message In User')
    module_fal_message_body_in_subtype = fields.Boolean(
        'Message Body in Subtype')
    module_fal_block_automatic_email = fields.Boolean(
        'Block Automatic Email')
    module_fal_internal_message = fields.Boolean(
        'Internal Message')
    module_fal_internal_email = fields.Boolean(
        'Internal Email')
    module_fal_hide_external_message = fields.Boolean(
        'Hide Odoo Default Send Message Button')
    module_validation_process = fields.Boolean(
        'Falinwa Validation Process')
    module_fal_model_activity = fields.Boolean(
        'Mail Activity Inheritance')
    module_fal_mail_debrand = fields.Boolean(
        'Do not show odoo branding on mail')

# Human Resource
    module_partner_firstname = fields.Boolean(
        'Partner First Name')

# Partner Management
    module_fal_partner_code = fields.Boolean(
        'Partner Code')
    module_fal_partner_private_address = fields.Boolean(
        'Private Address')
    module_fal_partner_qualification = fields.Boolean(
        'Partner Qualification')
    module_fal_partner_short_name = fields.Boolean(
        'Company Shortname')
    module_fal_partner_user_creation = fields.Boolean(
        'Partner User Creation')
    module_fal_dynamic_qualification = fields.Boolean(
        'Dynamic Qualification')
    module_fal_group_by_commercial = fields.Boolean(
        'Group By Commercial')

# Other
    module_web_hierarchy = fields.Boolean(
        'Hierarchial View')
    module_fal_change_background_company = fields.Boolean(
        'Change Company Background Image')
    module_fal_document_relation = fields.Boolean(
        'Document Relation to Record')

# New Base
    module_fal_contract_conditions = fields.Boolean(
        'Contract Conditions')
    module_fal_easy_reporting = fields.Boolean(
        'Dynamic Easy Reporting')
    module_fal_learning_resource = fields.Boolean(
        'Learning Resource')
    module_fal_partner_additional_info = fields.Boolean(
        'Partner Additional Info')
    module_fal_partner_quote = fields.Boolean(
        'Partner Quote')
    module_kanban_draggable = fields.Boolean(
        'Kanban Drag Drop Control')
    module_stoneware_customize = fields.Boolean(
        'Stoneware custom')
    module_theme_stoneware = fields.Boolean(
        'Theme Stoneware')
    module_web_tree_image = fields.Boolean(
        'Show images in tree views')
    module_fal_business_type = fields.Boolean(
        'Add business unit/type')
    module_fal_business_type_crm_ext = fields.Boolean(
        'Add business unit/type in crm')
    module_fal_business_type_sale_ext = fields.Boolean(
        'Add business unit/type in sale')
    module_fal_comment_template = fields.Boolean(
        'Comment Template')
    module_fal_tax_comment = fields.Boolean(
        'Tax Comment')
    module_fal_sale_line_comment = fields.Boolean(
        'Sale Line Comment')
    module_fal_global_object = fields.Boolean(
        'Global Object')


    @api.onchange('module_fal_partner_qualification')
    def _onchange_module_fal_partner_qualification(self):
        if self.module_fal_partner_qualification:
            self.module_fal_partner_qualification = True
