# -*- coding: utf-8 -*-
from odoo import api, models, fields


class hr_contract(models.Model):
    _inherit = "hr.contract"

    fal_is_prev_calendar_same = fields.Boolean(
        "Check if previous calendar and now calendar is the same",
        compute="_check_prev_calendar_calendar")

    @api.depends(
        'resource_calendar_id', 'employee_id',
        'employee_id.resource_calendar_id')
    @api.multi
    def _check_prev_calendar_calendar(self):
        for contract in self:
            if contract.employee_id.resource_calendar_id == contract.resource_calendar_id:
                contract.fal_is_prev_calendar_same = True
            else:
                contract.fal_is_prev_calendar_same = False

    @api.multi
    def change_fix_leave(self):
        for contract in self:
            if contract.employee_id.resource_calendar_id != contract.resource_calendar_id:
                contract.resource_calendar_id.autochangefixleave(
                    self.employee_id,
                    self.employee_id.resource_calendar_id,
                    self.resource_calendar_id
                )
            contract.employee_id.resource_calendar_id = contract.resource_calendar_id.id
            contract.employee_id.fal_previous_calendar = False

# end of hr_contract
