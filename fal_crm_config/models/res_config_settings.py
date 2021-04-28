# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Accounting
    module_fal_crm_multicurrency_group = fields.Boolean(
        'CRM MultiCurrency Group')

# New CRM
    module_fal_crm_ext = fields.Boolean(
        'CRM Extension')
    module_fal_crm_lead_project = fields.Boolean(
        'CRM: Opportunity to Project')
    module_fal_crm_wishlist = fields.Boolean(
        'CRM: Wishlist')
