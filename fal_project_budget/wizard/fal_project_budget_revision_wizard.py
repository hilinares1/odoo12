# -*- coding: utf-8 -*-
from odoo import models, api, _


class FalProjectBudgetRevisionWizard(models.TransientModel):
    _name = 'fal.project.budget.revision.wizard'
    _description = "Control Revision Wizard"

    @api.multi
    def action_project_budget_revision(self):
        self.ensure_one()
        new_id = False
        if self.env.context.get('active_id', False):
            fal_project_budget_obj = self.env['fal.project.budget']
            data = fal_project_budget_obj.browse(
                self.env.context.get('active_id', False))
            new_id = data.budget_revision()
        ref_id = 'fal_project_budget.fal_project_budget_view_form'
        view_id = self.env.ref(ref_id).id
        return {
            'name': _('Control'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.project.budget',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': new_id.id,
            'context': self.env.context,
            'target': 'current'
        }
