# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class FalTemplateBudgetFillDataWizard(models.TransientModel):
    _name = 'fal.template.budget.fill.data.wizard'
    _description = "Fill Data Wizard"

    fal_project_budget_id = fields.Many2one("fal.project.budget", string="Parent Control")
    fal_project_budget_ids = fields.Many2many("fal.project.budget", string="Control(s)")

    @api.multi
    def action_go_to_budget(self):
        self.ensure_one()
        if self.fal_project_budget_id:
            ref_id = 'fal_project_budget.fal_project_budget_view_form'
            view_id = self.env.ref(ref_id).id
            return {
                'name': _('Control'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fal.project.budget',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': self.fal_project_budget_id.id,
                'context': self.env.context,
                'target': 'current'
            }
