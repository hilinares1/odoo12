from odoo import fields, models, api
from odoo.tools.translate import _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class fal_periodic_allocation_wizard(models.TransientModel):
    _name = "fal.periodic.allocation.wizard"
    _description = 'Periodic Allocation'

    allocation_tmpl_ids = fields.One2many(
        comodel_name='fal.leave.allocation.template',
        inverse_name='wizard_id',
        string="Allocation Template",
        auto_join=True
        )
    holiday_status_id = fields.Many2one(
        "hr.leave.type", "Leave Type", required=True,
    )
    number_of_leaves = fields.Float(string="Number of Leaves", required=True, default=1)
    date_from = fields.Datetime('Run From', default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    date_to = fields.Datetime(
        'Run Until')
    number_per_interval = fields.Float(
        "Number of unit per interval", default=1)
    interval_number = fields.Integer(
        "Number of unit between two intervals", default=1)
    unit_per_interval = fields.Selection([
        ('hours', 'Hour(s)'),
        ('days', 'Day(s)')
    ],
        string="Unit of time added at each interval", default='hours')
    interval_unit = fields.Selection([
        ('weeks', 'Week(s)'),
        ('months', 'Month(s)'),
        ('years', 'Year(s)')
    ], string="Unit of time between two intervals", default='weeks')

    @api.onchange('date_from', 'date_to', 'number_of_leaves', 'number_per_interval'
                  'unit_per_interval', 'interval_number', 'interval_unit')
    def onchange_interval(self):
        allocation_obj = self.env['fal.leave.allocation.template']
        interval_number = self.interval_number or 1
        date_from = self.date_from

        for i in range(int(self.number_of_leaves)):
            if self.date_to and date_from > self.date_to:
                break

            allocation_obj += allocation_obj.create({
                'no': i+1,
                'date_to': self.date_to,
                'date_from': date_from,
                'number_of_days': 1,
                })

            if self.interval_unit == 'weeks':
                date_from = date_from + relativedelta(weeks=interval_number)
            if self.interval_unit == 'months':
                date_from = date_from + relativedelta(months=interval_number)
            if self.interval_unit == 'years':
                date_from = date_from + relativedelta(years=interval_number)

        self.allocation_tmpl_ids = allocation_obj

    @api.multi
    def periodic_leave_auto_create(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        employee_obj = self.env['hr.employee']
        resource_calendar_obj = self.env['resource.calendar']

        for all_wiz in self:
            allocation_ids = self.env['hr.leave.allocation']

            employee_ids = employee_obj.search(
                [('company_id', '=', resource_calendar_obj.browse(
                    active_id).company_id.id)])
            for employee_id in employee_ids.filtered(
                    lambda r: r.resource_calendar_id.id == active_id):
                # old way: create 1 allocation with x number_of_days
                # new : create x allocation with 1 number_of_days
                if not all_wiz.number_of_leaves:
                    break
                for alloc_tmpl in all_wiz.allocation_tmpl_ids:
                    alloc_vals = alloc_tmpl.prepare_allocation_vals()
                    alloc_vals.update({
                            'holiday_type': 'employee',
                            'employee_id': employee_id.id,
                            'fal_resource_calendar_id': active_id,
                        })
                    alloc_item = allocation_ids.create(alloc_vals)
                    # odoo override date_from field to be now
                    # it is wrong
                    # since some allocation may begin in different time
                    alloc_item.write({
                        'date_from': alloc_tmpl.date_from
                        })
                    allocation_ids += alloc_item
            # confirm allocation
            allocation_ids.action_confirm()
            allocation_ids.action_approve()
            alloc_test = allocation_ids.filtered(lambda hol: hol.validation_type == 'both')
            if all_wiz.holiday_status_id.validation_type == 'both':
                allocation_ids.action_validate()

# end of periodic_leave_auto_create()
