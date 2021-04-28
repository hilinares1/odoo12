# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class FalProjectBudgetFillT0Wizard(models.TransientModel):
    _name = 'fal.project.budget.fill.t0.wizard'
    _description = "Control Fill Wizard"

    @api.multi
    def action_project_budget_fill_t0(self):
        self.ensure_one()
        t0_total_budget = 0.00
        project_budget_obj = self.env['fal.project.budget']
        if self.env.context.get('active_id', False):
            project_list = project_budget_obj.search([
                ('id', '=', self.env.context.get('active_id', False))
            ])
            if not project_list.active:
                raise UserError(_('Please unarchive document first.'))
            for project in project_list:
                if project.type == 'root':
                    project.is_t0 = True
                for project_budget_line in project.fal_project_budget_line_ids:
                    project_budget_line.t0_planned_amount = project_budget_line.planned_amount
                    t0_total_budget += project_budget_line.planned_amount
                for child_project_budget in self.env['fal.project.budget'].search([('id', 'child_of', project.id), ('id', '!=', project.id)]):
                    self.with_context({'active_id': child_project_budget.id}).action_project_budget_fill_t0()
                for sub_budget in project.child_ids:
                    t0_total_budget += sub_budget.t0_total_budget
                project.t0_total_budget = t0_total_budget