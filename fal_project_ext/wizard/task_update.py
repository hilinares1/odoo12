import logging
from odoo import models, api, fields
_logger = logging.getLogger(__name__)


class ProjectTaskUpdate(models.TransientModel):
    _name = "project.task.update.wizard"
    _description = "Wizard for Project Task"

    name = fields.Char(string="Description")
    test_result = fields.Selection([
        ('pass', 'Pass'),
        ('fail', 'Fail')],
        string="Test Result", default='pass', required=True)
    current_stage_id = fields.Many2one(
        'project.task.type',
        string='Current Stage')
    next_stage_id = fields.Many2one(
        'project.task.type',
        string='Next Stage')
    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
        required=True, copy=False)
    user_id = fields.Many2one(
        'res.users',
        'Responsible',
        default=lambda self: self.env.user,
        readonly=True)
    next_assign = fields.Many2one('res.users', 'Next Action By')
    deadline = fields.Date(string="New Deadline", copy=False)

    @api.model
    def default_get(self, fields):
        res = super(ProjectTaskUpdate, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['current_stage_id'] = self.env['project.task'].search([(
                'id', '=', self.env.context['active_id'])],
                limit=1).stage_id.id
        return res

    @api.onchange('test_result')
    def onchange_next_stage(self):
        if self.test_result:
            current_stage_sequence = self.env['project.task'].search([('id', '=', self.env.context['active_id'])]).stage_id.sequence
            current_project_id = self.env['project.task'].search([('id', '=', self.env.context['active_id'])]).project_id.id
            project_stage_id = self.env['project.project'].search([('id', '=', current_project_id)]).type_ids

            if self.test_result == 'pass':
                fal_next_stage_id = self.env['project.task.type'].search(['&', ('sequence', '>', current_stage_sequence), ('id', 'in', project_stage_id.ids)], order='sequence asc', limit=1)
                return {'value': {'next_stage_id': fal_next_stage_id.id}}
            else:
                fal_next_stage_id = self.env['project.task.type'].search(['&', ('sequence', '<=', current_stage_sequence), ('id', 'in', project_stage_id.ids)], order='sequence desc')
                if fal_next_stage_id:
                    return {'domain': {'next_stage_id': [('id', 'in', fal_next_stage_id.ids)]}}

    @api.multi
    def action_update_task(self):
        context = dict(self._context)
        history = self.env['fal.history.change']
        task = self.env['project.task']
        active_id = context.get('active_id')
        res = task.browse(active_id)
        next_stage_id = False

        if self.test_result:
            current_stage_sequence = self.env['project.task'].search([('id', '=', self.env.context['active_id'])]).stage_id.sequence
            current_project_id = self.env['project.task'].search([('id', '=', self.env.context['active_id'])]).project_id.id
            project_stage_id = self.env['project.project'].search([('id', '=', current_project_id)]).type_ids

            if self.test_result == 'pass':
                fal_next_stage_id = self.env['project.task.type'].search(['&', ('sequence', '>', current_stage_sequence), ('id', 'in', project_stage_id.ids)], order='sequence asc', limit=1)
                next_stage_id = fal_next_stage_id.id
            else:
                next_stage_id = self.next_stage_id.id

        vals_history = {
            'task_id': res.id,
            'fal_date': self.date,
            'fal_status': self.test_result,
            'fal_desc': self.name,
            'fal_responsible': self.next_assign.id,
            'fal_stage_from': self.current_stage_id.id,
            'fal_stage_to': next_stage_id,
            'fal_new_deadline': self.deadline,
        }
        history = history.create(vals_history)

        val_task = {
            'fal_next_action_user_id': False,
            'user_id': self.next_assign.id or res.user_id.id or False,
            'stage_id': next_stage_id,
            'date_deadline': self.deadline or res.date_deadline or False,
        }
        res.write(val_task)
