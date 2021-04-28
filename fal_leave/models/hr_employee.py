from odoo import api, fields, models


class hr_employee(models.Model):
    _inherit = "hr.employee"

    fal_previous_calendar = fields.Many2one(
        'resource.calendar', 'Previous Working Hours'
    )
    # We need this so we can hide the button on form view
    fal_is_prev_calendar_calendar_same = fields.Boolean(
        "Check if previous calendar and now calendar is the same",
        compute="_check_prev_calendar_calendar")

    @api.depends('fal_previous_calendar', 'resource_calendar_id')
    @api.multi
    def _check_prev_calendar_calendar(self):
        for employee in self:
            if employee.fal_previous_calendar == employee.resource_calendar_id:
                employee.fal_is_prev_calendar_calendar_same = True
            else:
                employee.fal_is_prev_calendar_calendar_same = False

    @api.multi
    def write(self, vals):
        if vals.get('resource_calendar_id', False):
            if self.resource_calendar_id:
                vals.update({
                    'fal_previous_calendar': self.resource_calendar_id.id
                })
        return super(hr_employee, self).write(vals)

    @api.multi
    def change_fix_leave(self):
        for emp in self:
            if emp.resource_calendar_id:
                emp.resource_calendar_id.autochangefixleave(
                    self,
                    self.fal_previous_calendar,
                    self.resource_calendar_id
                )
