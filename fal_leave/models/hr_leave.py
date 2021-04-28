# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError, ValidationError


class hr_holidays(models.Model):
    _inherit = "hr.leave"

    # For Email Purpose
    def get_interval_date_from(self):
        date_res = self.date_from
        date_res = fields.Datetime.context_timestamp(self, date_res)
        date_res = fields.Datetime.to_string(date_res)
        return date_res

    def get_interval_date_to(self):
        date_res = self.date_to
        date_res = fields.Datetime.context_timestamp(self, date_res)
        date_res = fields.Datetime.to_string(date_res)
        return date_res

    @api.multi
    def _prepare_holiday_values(self, employee):
        values = super(hr_holidays, self)._prepare_holiday_values(employee)
        values['state'] = 'confirm'
        return values

    @api.multi
    def action_validate(self):
        # Ful override action_validate from hr.leave
        # it is required because we have new holiday_type working_hour
        # This new type must intercepted in the middle of the process
        for record in self:
            date_from_trx = record.request_date_from
            date_from_status = record.holiday_status_id.fal_period_out_departure_date
            date_to_trx = record.request_date_to
            date_to_status = record.holiday_status_id.fal_period_out_ending_date
            if date_to_status and date_from_status:
                if date_from_trx < date_from_status or date_to_trx > date_to_status:
                    raise UserError(_('Date Request should be between Period Out.'))

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if any(holiday.state not in ['confirm', 'validate1'] for holiday in self):
            raise UserError(_('Leave request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})
        self.filtered(lambda holiday: holiday.validation_type == 'both').write({'second_approver_id': current_employee.id})
        self.filtered(lambda holiday: holiday.validation_type != 'both').write({'first_approver_id': current_employee.id})

        for holiday in self.filtered(lambda holiday: holiday.holiday_type != 'employee'):
            if holiday.holiday_type == 'category':
                employees = holiday.category_id.employee_ids
            elif holiday.holiday_type == 'company':
                employees = self.env['hr.employee'].search([('company_id', '=', holiday.mode_company_id.id)])
            # override to support for holiday_type working_hour
            elif holiday.holiday_type == 'working_hour':
                employees = self.env['hr.employee'].search([('resource_calendar_id', '=', holiday.working_hour_id.id)])
            else:
                employees = holiday.department_id.member_ids

            if self.env['hr.leave'].search_count([('date_from', '<=', holiday.date_to), ('date_to', '>', holiday.date_from),
                               ('state', 'not in', ['cancel', 'refuse']), ('holiday_type', '=', 'employee'),
                               ('employee_id', 'in', employees.ids)]):
                raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

            values = [holiday._prepare_holiday_values(employee) for employee in employees]
            leaves = self.env['hr.leave'].with_context(
                tracking_disable=True,
                mail_activity_automation_skip=True,
                leave_fast_create=True,
            ).create(values)
            leaves.action_approve()
            # FIXME RLi: This does not make sense, only the parent should be in validation_type both
            if leaves and leaves[0].validation_type == 'both':
                leaves.action_validate()

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.activity_update()
        return True

    # By the end of year, we will change last year holiday as inactive / not visible
    @api.model
    def remove_remaining_leave(self):
        leave_type = self.env['hr.leave.type'].search(
            [
                ('fal_year', '<', datetime.date.today().strftime("%Y")),
                ('fal_year', '!=', '0000'),
            ])
        for holidays_status in leave_type:
            holidays_status.fal_employee_visible = False
            holidays_status.active = False

    # Odoo set holiday state in to approve, quite dangerous
    state = fields.Selection(default="draft")
    company_id = fields.Many2one(
        'res.company', 'Company id',
        default=lambda self: self.env.user.company_id)

    # We can have hidden holiday that cannot be requested / allocated
    holiday_status_id = fields.Many2one(
        domain="[('fal_employee_visible','=',True)]")
    fal_fix_holiday_line_id = fields.Many2one(
        'fal.fix.date', 'From Fix Date', readonly=True, ondelete="restrict")
    payslip_status_next_month = fields.Boolean(
        string='Reported in next payslips',
        help='Green this button when the leave has been \
        taken into account in the payslip.',
        default=False)

    # So manager can easily find his subordinate leave to approve
    fal_employee_manager_id = fields.Many2one(
        'hr.employee', related="employee_id.parent_id", store=True, string="Employee Manager")

    # add new holiday type
    working_hour_id = fields.Many2one(
        'resource.calendar', string="Working Hour")
    holiday_type = fields.Selection(
        selection_add=[('working_hour', 'By Working Hour')],
        help='By Employee: Allocation/Request for individual Employee, \
        By Employee Tag: Allocation/Request for group of employees in category, \
        By Working Hour: Allocation/Request for employee with specific working hour')

    _sql_constraints = [
        ('type_value',
         "CHECK((holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='working_hour' AND working_hour_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) )",
         "The employee, department, company, working hour, or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('date_check2', "CHECK ((date_from <= date_to))", "The start date must be anterior to the end date."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "If you want to change the number of days you should use the 'period' mode"),
    ]

    @api.onchange('holiday_type')
    def _onchange_type(self):
        super(hr_holidays, self)._onchange_type()
        if self.holiday_type == 'working_hour':
            self.employee_id = False
            self.mode_company_id = False
            self.department_id = False
            self.category_id = False
        else:
            self.working_hour_id = False

    @api.multi
    def toogle_payslip_status_next_month(self):
        if self.payslip_status_next_month:
            self.payslip_status_next_month = False
        else:
            self.payslip_status_next_month = True


class hr_holidays_allocat(models.Model):
    _inherit = "hr.leave.allocation"

    @api.multi
    def action_validate(self):
        date_now = fields.Date.today()
        for alloc in self:
            date_from_status = alloc.holiday_status_id.fal_period_out_departure_date
            date_to_status = alloc.holiday_status_id.fal_period_out_ending_date
            if date_to_status and date_from_status:
                if date_now < date_from_status or date_now > date_to_status:
                    raise UserError(_('Date Request should be between Period Out.'))
        res = super(hr_holidays_allocat, self).action_validate()
        return res

    # Odoo set holiday state in to approve, quite dangerous
    state = fields.Selection(default="draft")

    # We can have hidden holiday that cannot be requested / allocated
    holiday_status_id = fields.Many2one(
        domain="[('fal_employee_visible','=',True)]")

    fal_fix_holiday_line_id = fields.Many2one(
        'fal.fix.date', 'From Fix Date', readonly=True, ondelete="restrict")
    fal_resource_calendar_id = fields.Many2one(
        'resource.calendar', string="Working Hour")
    working_hour_id = fields.Many2one(
        'resource.calendar', string="Working Hour")

    holiday_type = fields.Selection(
        selection_add=[('working_hour', 'By Working Hour')],
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category"
             "\n- By Working Hour: employees of defined working hour")

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='working_hour' AND working_hour_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company, working hour, or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)", "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]

    def _action_validate_create_childs(self):
        childs = super(hr_holidays_allocat, self)._action_validate_create_childs()

        child_ext = self.env['hr.leave.allocation']
        if self.state == 'validate' and self.holiday_type in ['working_hour']:
            employees = self.env['hr.employee'].search([('resource_calendar_id', '=', self.working_hour_id.id)])
            for employee in employees:
                child_ext += self.with_context(
                    mail_notify_force_send=False,
                    mail_activity_automation_skip=True
                ).create(self._prepare_holiday_values(employee))

            child_ext.action_approve()
            if childs and self.holiday_status_id.validation_type == 'both':
                child_ext.action_validate()
        return childs + child_ext


    @api.multi
    def _prepare_holiday_values(self, employee):
        values = super(hr_holidays_allocat, self)._prepare_holiday_values(employee)
        values['state'] = 'confirm'
        return values


class hr_holidays_status(models.Model):
    _inherit = "hr.leave.type"

    @api.multi
    @api.constrains('fal_year')
    def _check_fal_year(self):
        for holiday_status in self:
            if holiday_status.fal_year \
                    and not holiday_status.fal_year.isdigit():
                raise ValueError(_('Year Must Contain Only Number!'))

    @api.multi
    @api.depends('name', 'fal_year')
    def name_get(self):
        res = super(hr_holidays_status, self).name_get()
        new_res = []
        for holiday_status in res:
            holiday_status_id = self.browse(holiday_status[0])
            if holiday_status_id.fal_year:
                new_res.append((holiday_status[0], holiday_status[1] + " [" + str(holiday_status_id.fal_year) + "]"))
            else:
                new_res.append((holiday_status[0], holiday_status[1]))
        return new_res

    # For managing purpose
    fal_year = fields.Char(
        string="Year",
        default=lambda self: datetime.date.today().strftime("%Y"))
    # We should add the constraints for this
    fal_period_in_departure_date = fields.Date(
        string="Allocation Period: Start Date")
    fal_period_in_ending_date = fields.Date(string="Allocation Period: End Date")
    fal_period_out_departure_date = fields.Date(
        string="Request Period: Start Date")
    fal_period_out_ending_date = fields.Date(string="Request Period: End Date")
    fal_employee_visible = fields.Boolean("Employee Visible", default=True)

# end of hr_holidays_status()
