from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.tools import float_utils
from dateutil import rrule
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    fal_latest_date = fields.Date(string='Date of Latest Version')
    fal_attachment = fields.Binary(
        string='Attachment', attachment=True,
        help="You can put working schedule contract / rule file here")
    fal_attachment_name = fields.Char(
        string='Attachment Name',
        help="You can put working schedule contract / rule file here")
    fal_allocation_ids = fields.One2many(
        "hr.leave.allocation",
        "fal_resource_calendar_id",
        string="Periodic Allocation")

    @api.multi
    def autochangefixleave(
            self, employee_id, prev_working_hour, new_working_hour):
        # Delete Previous Fix Leave
        if prev_working_hour:
            lastworkingschedule = prev_working_hour \
                and prev_working_hour.id or False
            fix_date_list_ids = self.env['fal.fix.date'].search(
                [
                    ('resource_calendar_id', '=', lastworkingschedule),
                    ('holiday_status_id.fal_year', '=', str(datetime.now().year)),
                ]).ids
            for holidays in self.env['hr.leave'].search(
                [
                    ('employee_id', '=', employee_id.id),
                    ('fal_fix_holiday_line_id', 'in', fix_date_list_ids)]):
                totaldays = holidays.number_of_days
                leave_allocation = self.env['hr.leave.allocation'].search(
                    [
                        ('employee_id', '=', employee_id.id),
                        ('holiday_status_id', '=', holidays.holiday_status_id.id),
                        ('number_of_days', '>=', 0),
                        ('fal_fix_holiday_line_id', 'in', fix_date_list_ids)],
                    limit=1)
                if leave_allocation:
                    if leave_allocation.number_of_days - totaldays <= 0:
                        if leave_allocation.state != 'draft':
                            if leave_allocation.state in [
                                    'cancel', 'refuse', 'confirm']:
                                leave_allocation.action_draft()
                            else:
                                leave_allocation.action_refuse()
                                leave_allocation.action_draft()
                        leave_allocation.unlink()
                if holidays.state != 'draft':
                    if holidays.state in ['cancel', 'refuse', 'confirm']:
                        holidays.action_draft()
                    else:
                        holidays.action_refuse()
                        holidays.action_draft()
                holidays.unlink()
        # Give Remaining Leave
        if new_working_hour:
            holiday_obj = self.env['hr.leave']
            list_fix_date = self.env['fal.fix.date'].search([
                ('resource_calendar_id', '=', new_working_hour.id),
                ('holiday_status_id.fal_year', '=', str(datetime.now().year)),
                ('state', '=', 'validate')
            ])
            for fix_date in list_fix_date:
                res = self.env['hr.leave.allocation'].create(
                    {
                        'fal_fix_holiday_line_id': fix_date.id,
                        'holiday_type': 'employee',
                        'employee_id': employee_id.id,
                        'holiday_status_id': fix_date.holiday_status_id.id,
                        'name': fix_date.name,
                        'number_of_days': fix_date.fal_days})
                if fix_date.holiday_status_id.validation_type == 'both':
                    res.action_confirm()
                    res.action_approve()
                    res.action_validate()
                else:
                    res.action_confirm()
                    res.action_approve()
                for fal_fix_date_line in fix_date.fal_fix_date_line_ids:
                    val_line = fal_fix_date_line
                    val_a = fix_date.holiday_status_id.id
                    val_b = val_line.fal_opening_date
                    val_c = val_line.fal_ending_date
                    val_g = val_line.fal_date_from
                    val_h = val_line.fal_date_to
                    res = holiday_obj.create(
                        {
                            'fal_fix_holiday_line_id': fix_date.id,
                            'holiday_type': 'employee',
                            'employee_id': employee_id.id,
                            'holiday_status_id': val_a,
                            'name': fix_date.name,
                            'date_from': val_b,
                            'date_to': val_c,
                            'request_date_from': val_g,
                            'request_date_to': val_h,
                            'number_of_days': fal_fix_date_line._get_number_of_days(
                                val_b, val_c,
                                employee_id.id),
                        })
                    if fix_date.holiday_status_id.validation_type == 'both':
                        res.action_confirm()
                        res.action_approve()
                        res.action_validate()
                    else:
                        res.action_confirm()
                        res.action_approve()
        employee_id.fal_previous_calendar = False
