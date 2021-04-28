# -*- coding: utf-8 -*-
from odoo import fields, models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_id = fields.One2many('project.project', related='analytic_account_id.project_ids', string='Project', readonly=False)
