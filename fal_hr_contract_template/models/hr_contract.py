from odoo import fields, models, api


class hr_contract(models.Model):
    _inherit = 'hr.contract'

    fal_contract_template_id = fields.Many2one(
        'hr.contract', string='Contract Template',
        domain=[('fal_is_template', '=', True)])
    fal_is_template = fields.Boolean(string="Is Template?")
    fal_timesheet_cost = fields.Monetary(
        string='Timesheet Cost', currency_field='currency_id',
        default=0.0, help="This is calculated from Wage / (4 * total hours per week), but you can change it yourself")

    @api.onchange('fal_contract_template_id')
    def _onchange_fal_contract_template_id(self):
        if not self.name:
            self.name = self.fal_contract_template_id.name
        if self.fal_contract_template_id:
            self.department_id = self.fal_contract_template_id.department_id.id
            self.type_id = self.fal_contract_template_id.type_id.id
            self.job_id = self.fal_contract_template_id.job_id.id
            self.resource_calendar_id = self.fal_contract_template_id.resource_calendar_id.id
            self.wage = self.fal_contract_template_id.wage
            self.advantages = self.fal_contract_template_id.advantages
            self.notes = self.fal_contract_template_id.notes
            self.struct_id = self.fal_contract_template_id.struct_id
            self.department_id = self.fal_contract_template_id.department_id.id
            self.job_id = self.fal_contract_template_id.job_id.id

    @api.onchange('resource_calendar_id', 'wage')
    def _onchange_fal_timesheet_cost(self):
        # Timesheet Cost is calculated in a month there are 4 weeks.
        # so you can get the same cost per hour every month.
        # Count Per week
        cost_per_week = 0.0
        if self.resource_calendar_id:
            for cal in self.resource_calendar_id.attendance_ids:
                cost_per_week += cal.hour_to - cal.hour_from
        # End dCount Per week
        cost = cost_per_week * 4
        self.fal_timesheet_cost = self.wage / cost


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # FIXME: this field should be in module hr_timesheet, not sale_timesheet
    timesheet_cost = fields.Monetary(
        string='Timesheet Cost', currency_field='currency_id',
        default=0.0, related='contract_id.fal_timesheet_cost')
