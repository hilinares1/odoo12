# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    fal_project_id = fields.Many2one(
        "project.project", "Project", copy=False)
    fal_task_id = fields.Many2one(
        "project.task", "Task", copy=False)
    fal_timesheet_created = fields.Boolean(copy=False)

    @api.multi
    def action_create_timesheet(self):
        context = {
            'default_attendee_ids': self.attendee_ids.ids,
            'default_fal_total_real_actual_duration': self.fal_total_real_actual_duration,
            'is_use_agenda': self.fal_use_agenda,
        }
        return {
            'name': _('Create Timesheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'meeting.timesheet.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def auto_create_timesheet(self):
        account_analytic_line_obj = self.env["account.analytic.line"]
        employee_obj = self.env["hr.employee"]
        start_datetime_format = self.start
        stop_datetime_format = self.stop
        if self.fal_project_id:
            effective = self.attendee_ids.filtered(
                lambda r: r.effective_presence is True)
            if not effective:
                raise UserError(_('Please confirm the effective presence'))
            for attendee in effective:
                if len(attendee.partner_id.user_ids) > 0:
                    employee_search = employee_obj.search([(
                        'user_id', 'in', attendee.partner_id.user_ids.ids)])
                    employee = employee_search and employee_search[0] or False
                    if employee:
                        if self.allday:
                            for num_of_day in range((
                                stop_datetime_format - start_datetime_format
                            ).days + 1):
                                time = datetime.timedelta(days=num_of_day)
                                _atts = employee.resource_calendar_id.attendance_ids
                                _cond1 = employee.resource_calendar_id
                                meeting_time = sum((
                                    resource_calendar_id.hour_to - resource_calendar_id.hour_from
                                ) for resource_calendar_id in _atts if _cond1 and
                                    int(resource_calendar_id.dayofweek) ==
                                    (start_datetime_format + time).weekday() or 0
                                )
                                time = datetime.timedelta(days=num_of_day)
                                account_analytic_line_obj.create({
                                    'date': start_datetime_format + time,
                                    'project_id': self.fal_project_id.id,
                                    'task_id': self.fal_task_id.id,
                                    'unit_amount': meeting_time,
                                    'name': self.name,
                                    'user_id': employee.user_id.id,
                                    'is_timesheet': True,
                                    'meeting_id': self.id
                                })
                        else:
                            start_date = self.start.date()
                            start_date_str = start_date
                            account_analytic_line_obj.create({
                                'date': start_date_str,
                                'project_id': self.fal_project_id.id,
                                'task_id': self.fal_task_id.id,
                                'unit_amount': self.fal_total_actual_duration if self.fal_use_agenda else self.fal_total_real_actual_duration,
                                'name': self.name,
                                'user_id': employee.user_id.id,
                                'is_timesheet': True,
                                'meeting_id': self.id
                            })
                    self.write({'fal_timesheet_created': True})

        else:
            raise UserError(_('Please set project to create timesheet'))

    @api.multi
    def button_action_draft(self):
        res = super(CalendarEvent, self).button_action_draft()
        for account_analytic_line in self.env['account.analytic.line'].search(
                [('meeting_id', '=', self.id)]):
            account_analytic_line.unlink()
        self.write({'fal_timesheet_created': False})
        return res

    @api.multi
    def unlink(self):
        for meeting in self:
            for acc_analytic_line in self.env['account.analytic.line'].search(
                    [('meeting_id', '=', meeting.id)]):
                acc_analytic_line.unlink()
        return super(CalendarEvent, self).unlink()
