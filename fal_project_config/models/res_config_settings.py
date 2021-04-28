# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

# Project
    module_fal_project_parent_account = fields.Boolean(
        'Project Parent Account')
# New Project
    module_fal_project_ext = fields.Boolean(
        'PJC-02_Project Extension')
    module_fal_project_search = fields.Boolean(
        'Project Search')