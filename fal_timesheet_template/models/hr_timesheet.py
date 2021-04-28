# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


FAL_DELTA_DAYS_FROM_MONDAY = {
    'monday': 0,
    'tuesday': 1,
    'wednesday': 2,
    'thursday': 3,
    'friday': 4,
    'saturday': 5,
    'sunday': 6,
}
val_d = FAL_DELTA_DAYS_FROM_MONDAY
INV_FAL_DELTADAYS_FROM_MONDAY = {v: k for k, v in val_d.items()}


class FalTimesheetTemplate(models.Model):
    _name = 'fal.timesheet.template'
    _description = "Timesheet Template"

    name = fields.Char('Name', size=64, required=1)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    fal_timesheet_template_line_ids = fields.One2many(
        'fal.timesheet.template.line',
        'fal_timesheet_template_id', 'Timesheet Template Line')
    week_line_ids = fields.One2many(
        'fal.timesheet.template.weekly.line', 'template_id', 'Weekly Line')
    template_type = fields.Selection(
        [('day', 'Day by Day'), ('week', 'Whole Week')],
        string="Type")
    is_auto = fields.Boolean(string="Is Automatic Update?")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.multi
    def write(self, vals):
        if not self.is_auto:
            if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
                raise UserError(
                    _('Only an HR Officer or Manager can update template.'))

        return super(FalTimesheetTemplate, self).write(vals)

    @api.multi
    def unlink(self):
        if not self.is_auto:
            if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
                raise UserError(
                    _('Only an HR Officer or Manager can update template.'))
        return super(FalTimesheetTemplate, self).unlink()
# end of FalTimesheetTemplate()


class FalTimesheetTemplateLine(models.Model):
    '''
        This object is used with "unlink" method
        behaviour in fal_set_done method of hr_timesheet.sheet object.
        Please don't make relationship (such as many2one)
        to this object to avoid Integrity Error.
    '''
    _name = 'fal.timesheet.template.line'
    _description = "Template Line"

    fal_timesheet_template_id = fields.Many2one(
        'fal.timesheet.template', 'Timesheet Template')
    project_id = fields.Many2one(
        'project.project', 'Project',
        domain="[('allow_timesheets', '=', True)]", required=1)
    unit_amount = fields.Float(
        'Quantity', default=0.0)
    week_id = fields.Many2one(
        'fal.timesheet.template.weekly.line', string='Day ID')
    task_id = fields.Many2one('project.task', string='Task')

# end of FalTimesheetTemplateLine()


class fal_timesheet_sheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.model
    def _default_fal_template(self):
        res = False
        emp_id = self.env['hr.employee'].search(
            [('user_id', '=', self._uid)], limit=1)
        group = self.env.ref('hr_timesheet.group_hr_timesheet_user')
        hr_user = [x.id for x in group.users]
        if emp_id:
            res = self.env['fal.timesheet.template'].search(
                [('employee_id', '=', emp_id.id)], limit=1).id or False
        if not res and self._uid not in hr_user:
            raise UserError(_(
                'You do not have any timesheet template. \
                Please contact your HR manager.'))
        return res

    fal_timesheet_template_id = fields.Many2one(
        'fal.timesheet.template', 'Timesheet Template',
        readonly=1,
        states={
            'draft': [('readonly', False)]},
        default=_default_fal_template)

    @api.onchange('fal_timesheet_template_id', 'date_start', 'date_end')
    def onchange_fal_timesheet_template_id(self):
        self.timesheet_ids = []
        lines = []
        template = self.fal_timesheet_template_id
        working_schedule = self.employee_id.resource_calendar_id
        working_days = []
        for days in working_schedule.attendance_ids:
            weekdays = days.dayofweek
            working_days.append(weekdays)
        if template.template_type == 'week':
            for template_line in template.fal_timesheet_template_line_ids:
                date = self.date_start
                # tambahan untuk unit_amount-->
                # disesuaikan dengan working schedule
                unit_amount = 0.0
                while date <= self.date_end:
                    day_date = str(date.weekday())
                    if day_date in working_days:
                        unit_amount = template_line.unit_amount
                        lines.append((0, 0, {
                            'date': date,
                            'project_id': template_line.project_id.id,
                            'unit_amount': unit_amount,
                            'name': template_line.project_id.name,
                            'user_id': self.user_id.id,
                            'is_timesheet': True,
                            'task_id': template_line.task_id.id or False,
                        }))
                    else:
                        lines.append((0, 0, {
                            'date': date,
                            'project_id': template_line.project_id.id,
                            'unit_amount': 0.0,
                            'name': template_line.project_id.name,
                            'user_id': self.user_id.id,
                            'is_timesheet': True,
                            'task_id': template_line.task_id.id or False,
                        }))
                    date += timedelta(days=1)
        elif template.template_type == 'day':
            for day_line in template.week_line_ids:
                day = day_line.day
                date = self.date_start
                delta_days = FAL_DELTA_DAYS_FROM_MONDAY.get(day, 0)
                for template_line in day_line.template_line_ids:
                    lines.append((0, 0, {
                        'date': date + timedelta(days=delta_days),
                        'project_id': template_line.project_id.id,
                        'unit_amount': template_line.unit_amount,
                        'name': template_line.project_id.name,
                        'user_id': self.user_id.id,
                        'is_timesheet': True,
                        'task_id': template_line.task_id.id or False,
                    }))
        self.timesheet_ids = lines

    @api.multi
    def action_to_timesheet_template(self):
        week_lines = []
        template_obj = self.env['fal.timesheet.template']
        dayline0_ids = []
        dayline1_ids = []
        dayline2_ids = []
        dayline3_ids = []
        dayline4_ids = []
        dayline5_ids = []
        dayline6_ids = []
        for date_ids in self.timesheet_ids:
            day = date_ids.date
            day_date = day.weekday()
            if day_date == 0:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline0_ids.append(dayline)
            elif day_date == 1:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline1_ids.append(dayline)
            elif day_date == 2:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline2_ids.append(dayline)
            elif day_date == 3:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline3_ids.append(dayline)
            elif day_date == 4:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline4_ids.append(dayline)
            elif day_date == 5:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline5_ids.append(dayline)
            elif day_date == 6:
                dayline = (0, 0, {
                    'project_id': date_ids.project_id and date_ids.project_id.id or False,
                    'task_id': date_ids.task_id and date_ids.task_id.id or False,
                    'unit_amount': date_ids.unit_amount,
                })
                dayline6_ids.append(dayline)

        if dayline0_ids:
            week_line = (0, 0, {
                'day': 'monday',
                'template_line_ids': dayline0_ids
            })
            week_lines.append(week_line)
        if dayline1_ids:
            week_line = (0, 0, {
                'day': 'tuesday',
                'template_line_ids': dayline1_ids
            })
            week_lines.append(week_line)
        if dayline2_ids:
            week_line = (0, 0, {
                'day': 'wednesday',
                'template_line_ids': dayline2_ids
            })
            week_lines.append(week_line)
        if dayline3_ids:
            week_line = (0, 0, {
                'day': 'thursday',
                'template_line_ids': dayline3_ids
            })
            week_lines.append(week_line)
        if dayline4_ids:
            week_line = (0, 0, {
                'day': 'friday',
                'template_line_ids': dayline4_ids
            })
            week_lines.append(week_line)
        if dayline5_ids:
            week_line = (0, 0, {
                'day': 'saturday',
                'template_line_ids': dayline5_ids
            })
            week_lines.append(week_line)
        if dayline6_ids:
            week_line = (0, 0, {
                'day': 'sunday',
                'template_line_ids': dayline6_ids
            })
            week_lines.append(week_line)
        vals = {
            'name': 'Template %s %s' % (self.employee_id.name, self.display_name),
            'employee_id': self.employee_id.id,
            'template_type': 'day',
            'is_auto': True,
            'week_line_ids': week_lines
        }
        template_obj.create(vals)
        return True

    @api.multi
    def action_timesheet_done(self):
        res = super(fal_timesheet_sheet, self).action_timesheet_done()
        template = self.fal_timesheet_template_id
        if template.is_auto:
            template_type = template.template_type
            lines = []
            week_lines = []
            if template_type == 'week':
                for old_line in template.fal_timesheet_template_line_ids:
                    old_line.unlink()
                for line in self.line_ids:
                    val_line = (0, 0, {
                        'project_id': line.project_id and line.project_id.id,
                    })
                    if val_line not in lines:
                        lines.append(val_line)

            elif template_type == 'day':
                for old_line in template.week_line_ids:
                    old_line.unlink()
                dayline0_ids = []
                dayline1_ids = []
                dayline2_ids = []
                dayline3_ids = []
                dayline4_ids = []
                dayline5_ids = []
                dayline6_ids = []
                for date_ids in self.timesheet_ids:
                    day = date_ids.date
                    day_date = day.weekday()
                    if day_date == 0:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline0_ids.append(dayline)
                    elif day_date == 1:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline1_ids.append(dayline)
                    elif day_date == 2:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline2_ids.append(dayline)
                    elif day_date == 3:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline3_ids.append(dayline)
                    elif day_date == 4:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline4_ids.append(dayline)
                    elif day_date == 5:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline5_ids.append(dayline)
                    elif day_date == 6:
                        dayline = (0, 0, {
                            'project_id': date_ids.project_id and date_ids.project_id.id or False,
                            'task_id': date_ids.task_id and date_ids.task_id.id or False,
                        })
                        dayline6_ids.append(dayline)

                if dayline0_ids:
                    week_line = (0, 0, {
                        'day': 'monday',
                        'template_line_ids': dayline0_ids
                    })
                    week_lines.append(week_line)
                if dayline1_ids:
                    week_line = (0, 0, {
                        'day': 'tuesday',
                        'template_line_ids': dayline1_ids
                    })
                    week_lines.append(week_line)
                if dayline2_ids:
                    week_line = (0, 0, {
                        'day': 'wednesday',
                        'template_line_ids': dayline2_ids
                    })
                    week_lines.append(week_line)
                if dayline3_ids:
                    week_line = (0, 0, {
                        'day': 'thursday',
                        'template_line_ids': dayline3_ids
                    })
                    week_lines.append(week_line)
                if dayline4_ids:
                    week_line = (0, 0, {
                        'day': 'friday',
                        'template_line_ids': dayline4_ids
                    })
                    week_lines.append(week_line)
                if dayline5_ids:
                    week_line = (0, 0, {
                        'day': 'saturday',
                        'template_line_ids': dayline5_ids
                    })
                    week_lines.append(week_line)
                if dayline6_ids:
                    week_line = (0, 0, {
                        'day': 'sunday',
                        'template_line_ids': dayline6_ids
                    })
                    week_lines.append(week_line)
            vals = {
                'fal_timesheet_template_line_ids': lines,
                'week_line_ids': week_lines
            }
            template.write(vals)
        return res

# end of hr_timesheet_sheet()


class FalTimesheetTemplateWeeklyLine(models.Model):
    _name = 'fal.timesheet.template.weekly.line'
    _description = "Timesheet Template Weekly"

    @api.depends('template_line_ids')
    def _get_name_lines(self):
        for item in self:
            names = ''
            for line in item.template_line_ids:
                project = line.project_id
                name = project.name or ''
                val_p = project.partner_id.commercial_partner_id.name
                if project.partner_id:
                    name = name + ' - ' + val_p
                if len(item.template_line_ids) > 1:
                    names = name + '; ' + names
                elif len(item.template_line_ids) == 1:
                    names = name
            item.template_line_name = names

    day = fields.Selection([
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday')
    ], string='Day')
    template_line_ids = fields.One2many(
        'fal.timesheet.template.line', 'week_id', string='Template Line Name')
    template_id = fields.Many2one('fal.timesheet.template', string='Template')
    template_line_name = fields.Char(
        compute='_get_name_lines', string='Template Line')
