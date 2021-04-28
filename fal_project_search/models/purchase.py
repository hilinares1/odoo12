# -*- coding: utf-8 -*-
from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    account_analytic_id = fields.Many2one('account.analytic.account', related='order_line.account_analytic_id', string='Analytic Account', readonly=False)
    project_ids = fields.One2many('project.project', related='order_line.account_analytic_id.project_ids', string='Project', readonly=False)
