# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang
import logging

_logger = logging.getLogger(__name__)


class MeetingTimesheetWizard(models.TransientModel):
    _name = 'meeting.timesheet.wizard'
    _description = "Create timesheet from meeting"

    fal_total_real_actual_duration = fields.Float(
        "Total Actual Duration")
    attendee_ids = fields.Many2many('calendar.attendee', string="Invitation")

    def create_timesheet(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        calendar_obj = self.env['calendar.event']
        calendar = calendar_obj.browse(active_id)
        calendar.fal_total_real_actual_duration = self.fal_total_real_actual_duration
        calendar.auto_create_timesheet()
