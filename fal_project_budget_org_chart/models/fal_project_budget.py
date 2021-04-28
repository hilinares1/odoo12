# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FalProjectBudget(models.Model):
    _name = 'fal.project.budget'
    _inherit = "fal.project.budget"

    # child_for_chart_ids = 
    parent_for_chart_id = fields.Many2one('fal.project.budget', 'Parent Control For Chart', related='parent_id', store=True, readonly=True)
    child_for_chart_ids = fields.One2many('fal.project.budget', 'parent_for_chart_id', 'Child Control For Chart', related='child_ids', store=True, readonly=True)

    child_all_count = fields.Integer(
        'Indirect Surbordinates Count',
        compute='_compute_child_all_count', store=False)

    @api.depends('child_ids.child_all_count')
    def _compute_child_all_count(self):
        for fal_project_budget in self:
            fal_project_budget.child_all_count = len(fal_project_budget.child_ids) + sum(child.child_all_count for child in fal_project_budget.child_ids)
