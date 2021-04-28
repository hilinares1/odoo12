# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    fal_project_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        company_dependent=True
    )
