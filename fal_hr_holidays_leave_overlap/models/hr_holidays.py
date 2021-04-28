# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class HrHolidays(models.Model):
    _inherit = 'hr.leave'

    fal_linked_holiday_ids = fields.Many2many(
        comodel_name="hr.leave", relation="fal_leave_rel",
        column1="fal_main_linked_holidays_ids", column2="fal_main_linked_holidays",
        readonly=True
    )

    def action_approve_linked_holidays(self):
        for leave in self.fal_linked_holiday_ids:
            if leave.state == 'confirm':
                leave.action_approve()
            elif leave.state == 'draft':
                raise ValidationError(_('Please Submit the leaves to approve all linked holidays!'))
        self.action_approve()

    def action_confirm_linked_holidays(self):
        for leave in self.fal_linked_holiday_ids:
            if leave.state == 'draft':
                leave.action_confirm()
        self.action_confirm()

    def _fal_left_overlapping(self, employee_id, date_to, date_from):
        left_overlapping = self.search([
            ('date_from', '<=', date_from),
            ('date_to', '>=', date_from),
            ('date_to', '<', date_to),
            ('employee_id', '=', employee_id),
            ('state', 'not in', ['cancel', 'refuse']),
        ], limit=1)
        return left_overlapping

    def _fal_included(self, employee_id, date_to, date_from):
        included = self.search([
            ('date_from', '>', date_from),
            ('date_to', '<', date_to),
            ('employee_id', '=', employee_id),
            ('state', 'not in', ['cancel', 'refuse']),
        ], order='date_from ASC')
        return included

    def _fal_right_overlapping(self, employee_id, date_to, date_from):
        right_overlapping = self.search([
            ('date_from', '>', date_from),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_to),
            ('employee_id', '=', employee_id),
            ('state', 'not in', ['cancel', 'refuse']),
        ], limit=1)
        return right_overlapping

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):
        super(HrHolidays, self)._onchange_leave_dates()

        leave_overlap = []
        left_overlapping = self._fal_left_overlapping(self.employee_id.id, self.date_to, self.date_from)
        if left_overlapping:
            leave_overlap.append(left_overlapping.id)

        included = self._fal_included(self.employee_id.id, self.date_to, self.date_from)

        if included:
            leave_overlap.append(included.id)

        right_overlapping = self._fal_right_overlapping(self.employee_id.id, self.date_to, self.date_from)

        if right_overlapping:
            leave_overlap.append(right_overlapping.id)

        res = {}
        if leave_overlap:
            res['warning'] = {
                'title': _("Warning"),
                'message': 'You have leaves that overlaps on the same day. this leaves will split'
            }
        return res

    @api.model
    def create(self, values):
        leave_rel = []
        including = self.search([
            ('date_from', '<', values['date_from']),
            ('date_to', '>', values['date_to']),
            ('employee_id', '=', values['employee_id']),
            ('state', 'not in', ['cancel', 'refuse']),
        ], limit=1)
        if including:
            raise ValidationError(_(
                'You are trying to create a leave on a period which is '
                'already completely covered by a different leave!')
            )

        base_date = [values['date_from'], values['date_to']]
        split_date = []
        stepping_date = []

        left_overlapping = self._fal_left_overlapping(values['employee_id'], values['date_to'], values['date_from'])
        if left_overlapping:
            leave_rel.append(left_overlapping.id)

        for leave in left_overlapping:
            base_date[0] = fields.Datetime.to_string(leave.date_to.replace(hour=leave.date_from.hour) + timedelta(hours=24))

        included = self._fal_included(values['employee_id'], values['date_to'], values['date_from'])

        if included:
            leave_rel.append(included.id)

        for leave in included:
            if not stepping_date and base_date[0] == fields.Datetime.to_string(leave.date_from):
                base_date[0] = fields.Datetime.to_string(leave.date_to + timedelta(hours=24))
                continue

            s_date = stepping_date and stepping_date[-1] or base_date[0]
            e_date = fields.Datetime.to_string(leave.date_from.replace(hour=leave.date_to.hour) - timedelta(hours=24))
            split_date.append((s_date, e_date))
            stepping_date.append(fields.Datetime.to_string(leave.date_to + timedelta(hours=24)))

        right_overlapping = self._fal_right_overlapping(values['employee_id'], values['date_to'], values['date_from'])

        if right_overlapping:
            leave_rel.append(right_overlapping.id)
            base_date[1] = fields.Datetime.to_string(right_overlapping.date_from.replace(hour=right_overlapping.date_to.hour) - timedelta(hours=24))
            if stepping_date:
                split_date.append(stepping_date[-1], base_date[1])
        if stepping_date and split_date:
            stepping_date_convert = fields.datetime.strptime(stepping_date[-1], DEFAULT_SERVER_DATETIME_FORMAT)
            base_date_convert = fields.datetime.strptime(base_date[0], DEFAULT_SERVER_DATETIME_FORMAT)
            new_stepping_date = stepping_date_convert.replace(hour=base_date_convert.hour)
            split_date.append((new_stepping_date, base_date[1]))

        if not split_date:
            split_date.append(base_date)

        for period in split_date:
            new_vals = values.copy()
            new_vals['date_from'] = period[0]
            new_vals['date_to'] = period[1]
            new_vals['request_date_from'] = period[0]
            new_vals['request_date_to'] = period[1]
            res = super(HrHolidays, self).create(new_vals)
            res._onchange_leave_dates()
            leave_rel.append(res.id)

        leave_merge = self.browse(leave_rel)
        for item in leave_merge:
            leave = leave_merge.filtered(lambda a: a.id != item.id)
            item.fal_linked_holiday_ids = [(6, 0, leave.ids)]
        return res
