# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_tt_t0_project_budget_id(self):
        for line in self:
            line.tt_t0_project_budget_id = \
                self.env['fal.project.budget'].search([
                    ('project_id', '=', line.id),
                    ('is_t0', '=', True),
                ], limit=1).id

    @api.multi
    def _compute_tt_validated_project_budget_id(self):
        for line in self:
            line.tt_validated_project_budget_id = \
                self.env['fal.project.budget'].search([
                    ('project_id', '=', line.id),
                    ('state', 'in', ['validate', 'done']),
                    ('active', '=', True)
                ], limit=1).id

    tt_t0_project_budget_id = fields.Many2one('fal.project.budget', compute="_compute_tt_t0_project_budget_id", string='T0 Control')
    tt_validated_project_budget_id = fields.Many2one('fal.project.budget', compute="_compute_tt_validated_project_budget_id", string='Validated Control')

# end of ProjectProject()
