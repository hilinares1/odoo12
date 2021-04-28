# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class HrTmesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    @api.multi
    def action_timesheet_confirm(self):
        # Check by Sudo, as we don't want to change anything on the security side
        self.sudo()._check_hour()
        return super(HrTmesheetSheet, self).action_timesheet_confirm()

    @api.multi
    def _check_hour(self):
        for sheet in self:
            # Check if they reach weekly minimal workhours or not
            _total_hours = 0.0
            for line in sheet.timesheet_ids:
                _total_hours += line.unit_amount

            if sheet.employee_id.contract_id and sheet.employee_id.contract_id.resource_calendar_id.fal_is_set_week_minimum_hour:
                if _total_hours < sheet.employee_id.contract_id.resource_calendar_id.fal_week_minimal_hour:
                    raise UserError(_('This timesheet is below your minimum \
                        weekly working hours. Please fix your timesheet'))

            if sheet.employee_id.contract_id and sheet.employee_id.contract_id.resource_calendar_id.fal_is_set_week_maximal_hour:
                if _total_hours > sheet.employee_id.contract_id.resource_calendar_id.fal_week_maximal_hour:
                    raise UserError(_('This timesheet is over from your maximum \
                        weekly working hours. Please fix your timesheet'))

            if sheet.employee_id.contract_id and sheet.employee_id.contract_id.resource_calendar_id.fal_is_set_week_equal_hour:
                if _total_hours != sheet.employee_id.contract_id.resource_calendar_id.fal_week_equal_hour:
                    raise UserError(_('This timesheet is not same with your equal \
                        weekly working hours. Please fix your timesheet'))
