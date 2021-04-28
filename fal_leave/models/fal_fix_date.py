# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import math
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time


class fal_fix_date(models.Model):
    _name = "fal.fix.date"
    _description = 'Fixed Date'

    name = fields.Char(string="Name", required=True)
    fal_days = fields.Float(string="Total Days", compute="_compute_days")
    resource_calendar_id = fields.Many2one(
        'resource.calendar', string="Resource Calendar", required=True)
    holiday_status_id = fields.Many2one(
        "hr.leave.type", "Leave Type", required=True,
    )
    fal_fix_date_line_ids = fields.One2many(
        "fal.fix.date.line",
        "fal_fix_date_id",
        string="Fixed Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validate', 'Validate')], 'State',
        default="draft", required=True)

    def _compute_days(self):
        totaldays = 0
        for item in self:
            for line in item.fal_fix_date_line_ids:
                totaldays += line._get_number_of_days(
                    line.fal_opening_date,
                    line.fal_ending_date, False)
            item.fal_days = totaldays

    @api.multi
    def leave_auto_create(self):
        employee_obj = self.env['hr.employee']
        holiday_obj = self.env['hr.leave']
        holiday_allocation_obj = self.env['hr.leave.allocation']
        for all_fix_date in self.filtered(lambda r: r.state == 'draft'):
            this_working_schedule_id = all_fix_date.resource_calendar_id
            employee_ids = employee_obj.search(
                [('company_id', '=', this_working_schedule_id.company_id.id)])
            temp_allocation = {
                'res_first_validation': holiday_allocation_obj,
                'res_double_validation': holiday_allocation_obj}
            temp_request = {
                'res_first_validation': holiday_obj,
                'res_double_validation': holiday_obj}
            val_x = this_working_schedule_id.id
            for employee_id in employee_ids.filtered(
                    lambda r: r.resource_calendar_id.id == val_x):
                res_allocation = holiday_allocation_obj.create(
                    {
                        'fal_fix_holiday_line_id': all_fix_date.id,
                        'holiday_type': 'employee',
                        'employee_id': employee_id.id,
                        'holiday_status_id': all_fix_date.holiday_status_id.id,
                        'name': all_fix_date.name,
                        'number_of_days': all_fix_date.fal_days,
                    })
                if all_fix_date.holiday_status_id.validation_type == 'both':
                    temp_allocation['res_double_validation'] += res_allocation
                else:
                    temp_allocation['res_first_validation'] += res_allocation
                for key, value in temp_allocation.items():
                    for x in value:
                        if x.state == 'draft':
                            if key == 'res_first_validation':
                                x.action_confirm()
                                x.action_approve()
                            else:
                                x.action_confirm()
                                x.action_approve()
                                x.action_validate()
                for x in all_fix_date.fal_fix_date_line_ids:
                    val_a = all_fix_date.holiday_status_id.id
                    res_leave = holiday_obj.create(
                        {
                            'fal_fix_holiday_line_id': all_fix_date.id,
                            'holiday_type': 'employee',
                            'employee_id': employee_id.id,
                            'holiday_status_id': val_a,
                            'name': all_fix_date.name,
                            'date_from': x.fal_opening_date,
                            'date_to': x.fal_ending_date,
                            'request_date_from': x.fal_date_from,
                            'request_date_to': x.fal_date_to,
                            'number_of_days': x._get_number_of_days(
                                x.fal_opening_date, x.fal_ending_date,
                                employee_id.id),
                        })
                    if all_fix_date.holiday_status_id.validation_type == 'both':
                        temp_request['res_double_validation'] += res_leave
                    else:
                        temp_request['res_first_validation'] += res_leave
            for key, value in temp_request.items():
                for x in value:
                    if x.state == 'draft':
                        if key == 'res_first_validation':
                            x.action_confirm()
                            x.action_approve()
                        else:
                            x.action_confirm()
                            x.action_approve()
                            x.action_validate()
            all_fix_date.state = 'validate'


class fal_fix_date_line(models.Model):
    _name = "fal.fix.date.line"
    _description = 'Fix Date Line'

    fal_fix_date_id = fields.Many2one("fal.fix.date", "Fixed Date")
    fal_opening_date = fields.Datetime(string="Opening Date",)
    fal_ending_date = fields.Datetime(string="Ending Date")
    fal_date_from = fields.Date(string="Date From")
    fal_date_to = fields.Date(string="Date To")

    @api.onchange('fal_date_from', 'fal_date_to')
    def _onchange_date(self):
        if self.fal_date_from and self.fal_date_to:
            domain = [('calendar_id', '=', self.fal_fix_date_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
            attendances = self.env['resource.calendar.attendance'].search(
                domain, order='dayofweek, day_period DESC')

            # find first attendance coming after first_day
            attendance_from = next((
                att for att in attendances if int(
                    att.dayofweek
                ) >= self.fal_date_from.weekday()), attendances[0])
            # find last attendance coming before last_day
            attendance_to = next((
                att for att in reversed(
                    attendances
                ) if int(
                    att.dayofweek
                ) <= self.fal_date_to.weekday()), attendances[-1])

            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

            tz = self.env.user.tz if self.env.user.tz else 'UTC'
            self.fal_opening_date = timezone(tz).localize(
                datetime.combine(self.fal_date_from, hour_from)
            ).astimezone(UTC).replace(tzinfo=None)
            self.fal_ending_date = timezone(tz).localize(
                datetime.combine(self.fal_date_to, hour_to)
            ).astimezone(UTC).replace(tzinfo=None)

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            return employee.get_work_days_data(date_from, date_to)['days']

        time_delta = date_to - date_from
        return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
