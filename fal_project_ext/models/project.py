# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = 'project.project'

    project_opportunities = fields.Boolean(string='Opportunities')
    description = fields.Text('Description')
    code = fields.Char('Code', size=12)

    #  default project merge from fal_project_module_version

    @api.model
    def create(self, vals):
        if vals.get('project_opportunities'):
            project_task_type = self.env['project.task.type']\
                .search([('sequence', '!=', None),
                         ('project_opportunities_default', '=', 1)])
            id_project_task_type_list = []
            for id_project_task_type in project_task_type:
                id_project_task_type_list.append(id_project_task_type.id)

            vals['type_ids'] = [(6, 0, id_project_task_type_list)]
            res = super(Project, self).create(vals)
            return res

        else:

            project_task_type = self.env['project.task.type']\
                .search([('sequence', '!=', None),
                         ('case_default', '=', 1)])
            id_project_task_type_list = []
            for id_project_task_type in project_task_type:
                id_project_task_type_list.append(id_project_task_type.id)

            vals['type_ids'] = [(6, 0, id_project_task_type_list)]
            res = super(Project, self).create(vals)
            return res

    @api.multi
    def modify_defauly_stage(self, vals):
        if self.project_opportunities:
            project_task_type = self.env['project.task.type']\
                .search([('sequence', '!=', None),
                         ('project_opportunities_default', '=', 1)])
            id_project_task_type_list = []
            for id_project_task_type in project_task_type:
                id_project_task_type_list.append(id_project_task_type.id)
            vals['type_ids'] = [(6, 0, id_project_task_type_list)]
            res = super(Project, self).write(vals)
            return res
        else:
            project_task_type = self.env['project.task.type']\
                .search([('sequence', '!=', None),
                         ('case_default', '=', 1)])
            id_project_task_type_list = []
            for id_project_task_type in project_task_type:
                id_project_task_type_list.append(id_project_task_type.id)

            vals['type_ids'] = [(6, 0, id_project_task_type_list)]
            res = super(Project, self).write(vals)
            return res


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    project_opportunities_default = fields.Boolean(
        string='Default for Project Opportunities',
        help='If you check this field, this stage will be proposed by default \
        on each new Project Opportunities. It will not assign this stage to\
        existing Project Opportunities.')
    case_default = fields.Boolean(
        string='Default for New Projects',
        help='If you check this field, this stage will be proposed by default on \
        each new project. It will not assign this stage to existing projects.')


class Task(models.Model):
    _inherit = 'project.task'

    project_id_partner_id = fields.Many2one('res.partner', related='project_id.partner_id', string='Final Customer', readonly=True, store=True)
    # merge from fal_project_module_version
    fal_next_action_user_id = fields.Many2one('res.users', string='Next Action by')
    fal_responsible_user_id = fields.Many2one('res.users', string='Responsible')
    fal_cust_deadline = fields.Date(string='Customer Deadline')
    fal_change_ids = fields.One2many('fal.history.change', 'task_id', string='Change History')
    task_relation = fields.Many2one('project.task', 'Task Relation')
    priority = fields.Selection(selection_add=[
        ('2', 'High'),
        ('3', 'Urgent')
    ])

    @api.multi
    def action_cancel(self):
        stage_cancel = self.env['project.task.type'].search([
            ('name', '=', 'Cancel')], limit=1).id
        self.stage_id = stage_cancel
        self.fal_same_level = True

    @api.multi
    def action_update(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'project.task.update.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class HistoryChange(models.Model):
    _name = "fal.history.change"
    _description = "Task History Change"

    task_id = fields.Many2one("project.task", "Task")
    fal_date = fields.Datetime(string='Date')
    fal_desc = fields.Text(string='Description')
    fal_responsible = fields.Many2one('res.users', string='Responsible')
    fal_stage_from = fields.Many2one('project.task.type', string='From Stage')
    fal_stage_to = fields.Many2one('project.task.type', string='To Stage')
    fal_date_deadline = fields.Date(string='Deadline')
    fal_new_deadline = fields.Date(string='New Deadline')
    fal_status = fields.Text(string='Status')
