# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    account_analytic_id = fields.Many2one('account.analytic.account', related='invoice_line_ids.account_analytic_id', string='Analytic Account', readonly=False)
    project_ids = fields.One2many('project.project', related='invoice_line_ids.account_analytic_id.project_ids', string='Project', readonly=False)