from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class hr_holidays_postpone_wizard(models.TransientModel):
    _name = "hr.holidays.postpone.wizard"
    _description = "Holidays Postpone"

    holidays_status_id = fields.Many2one(
        'hr.leave.type',
        string='Leave Type',
        default=lambda self: self.env.context['active_ids'][0])
    lost_days_reason = fields.Selection(
        [
            ('pu', 'Lost Leave - PU'),
            ('py', 'Lost Leave - PY')
        ],
        string="Lost Days Reason",
        default="pu",
        required=True)
    description = fields.Char(string="Description", required=True)
    postpone_line = fields.One2many(
        'hr.holidays.postpone.wizard.line', 'postpone_id')

    @api.multi
    def postpone_holidays(self):
        for employee in self.postpone_line:
            duration = 0
            search = [
                ('holiday_status_id', '=', self.holidays_status_id.id),
                ('employee_id', '=', employee.employee_id.id)]
            for leave_allocation in self.env['hr.leave.allocation'].search(search):
                if leave_allocation.state in [
                        'validate', 'validate1']:
                    duration += leave_allocation.number_of_days
            for leave in self.env['hr.leave'].search(search):
                if leave.state in [
                        'validate', 'validate1']:
                    duration -= leave.number_of_days
            if self.holidays_status_id \
                    and employee.employee_id \
                    and duration >= employee.duration and duration > 0:
                for leave in self.env['hr.leave.allocation'].search([
                    ('holiday_status_id', '=', self.holidays_status_id.id),
                    ('employee_id', '=', employee.employee_id.id),
                    ('state', 'in', ['validate', 'validate1'])
                ]):
                    if duration > 0:
                        if duration >= leave.number_of_days:
                            duration -= leave.number_of_days
                            leave.action_refuse()
                        else:
                            leave.number_of_days -= duration
                            duration = 0
                if self.lost_days_reason == 'pu':
                    val_c = self.env.ref('fal_leave.fal_hr_holidays_status_1')
                    self.env['hr.leave.allocation'].create(
                        {
                            'number_of_days': employee.duration,
                            'holiday_status_id': val_c.id,
                            'name': self.description,
                            'employee_id': employee.employee_id.id,
                            'holiday_type': 'employee',
                            'state': 'validate'})
                elif self.lost_days_reason == 'py':
                    val_d = self.env.ref('fal_leave.fal_hr_holidays_status_2')
                    self.env['hr.leave.allocation'].create(
                        {
                            'number_of_days': employee.duration,
                            'holiday_status_id': val_d.id,
                            'name': self.description,
                            'employee_id': employee.employee_id.id,
                            'holiday_type': 'employee',
                            'state': 'validate'})
            else:
                raise UserError(
                    _("This Employee Doesn't have \
                        Sufficient Holidays to Postpone!"))


class hr_holidays_postpone_wizard_line(models.TransientModel):
    _name = "hr.holidays.postpone.wizard.line"
    _description = "Holidays Postpone Line"

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True)
    department_id = fields.Many2one(
        'hr.department',
        related="employee_id.department_id",
        string="Department")
    duration = fields.Float(string="Duration", required=True)
    postpone_id = fields.Many2one('hr.holidays.postpone.wizard')

    @api.multi
    @api.onchange(
        'employee_id')
    def onchange_remaining_leave(self):
        for postpone_wizard in self:
            duration = 0
            search = [
                ('holiday_status_id', '=', postpone_wizard.postpone_id.holidays_status_id.id),
                ('employee_id', '=', postpone_wizard.employee_id.id)]
            for leave_allocation in self.env['hr.leave.allocation'].search(search):
                if leave_allocation.state in [
                        'validate', 'validate1']:
                    duration += leave_allocation.number_of_days
            for leave in self.env['hr.leave'].search(search):
                if leave.state in [
                        'validate', 'validate1']:
                    duration -= leave.number_of_days
            self.duration = duration


# end of hr_holidays_postpone_wizard()
