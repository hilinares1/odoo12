# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_fal_project_budget_org_chart = fields.Boolean(string="Show Organizational Chart")
    module_fal_project_dashboard = fields.Boolean(string="Controlling Dashboard")
