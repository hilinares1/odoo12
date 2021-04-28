from odoo import fields, models, api
from odoo.tools.translate import _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from dateutil.relativedelta import relativedelta


class FalLeaveAllocationTemplate(models.TransientModel):
    _name = "fal.leave.allocation.template"
    _description = 'Leave Allocation Template'

    wizard_id = fields.Many2one(
        comodel_name='fal.periodic.allocation.wizard', string='Wizard'
    )
    no = fields.Integer('No', help="field helper to display template number in treeview")
    date_from = fields.Datetime('Start Date')
    date_to = fields.Datetime('End Date')

    def prepare_allocation_vals(self):
        return {
            'state': 'draft',
            'accrual': True,
            'holiday_status_id': self.wizard_id.holiday_status_id.id,
            'number_of_days': 1,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'number_per_interval': self.wizard_id.number_per_interval,
            'unit_per_interval': self.wizard_id.unit_per_interval,
            'interval_unit': self.wizard_id.interval_unit
        }

# end of periodic_leave_auto_create()
