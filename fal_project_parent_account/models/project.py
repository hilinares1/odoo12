# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = "project.project"

    project_type = fields.Selection(
        [('view', 'Project View'),
         ('normal', 'Normal')],
        string='Type of Project', default='normal')

    parent_id = fields.Many2one(
        'project.project',
        'Parent Account',
        domain="[('project_type', '=', 'view')]",
        ondelete='restrict')

    @api.model
    def create(self, values):
        res = super(Project, self).create(values)
        allow_timesheets = values['allow_timesheets'] if 'allow_timesheets' in values else self.default_get(['allow_timesheets'])['allow_timesheets']
        if allow_timesheets:
            analytic = values.get('analytic_account_id')
            analytic_account = self.env['account.analytic.account'].browse(analytic)
            if values.get('project_type'):
                analytic_account.write({'account_type': values.get('project_type')})
        return res

# end of Project()
