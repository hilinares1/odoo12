from odoo import api, fields, models, _


class Sheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    def _get_timesheet_sheet_lines_domain(self):
        self.ensure_one()
        # Full Override
        # Without Thinking the company
        return [
            ('project_id', '!=', False),
            ('date', '<=', self.date_end),
            ('date', '>=', self.date_start),
            ('employee_id', '=', self.employee_id.id),
        ]

    @api.constrains('company_id')
    def _check_company_id(self):
        # No need to check company compatibility
        return True

    @api.onchange('add_line_project_id')
    def onchange_add_project_id(self):
        """Load the project to the timesheet sheet"""
        # Full Override
        # Without Thinking the company
        if self.add_line_project_id:
            return {
                'domain': {
                    'add_line_task_id': [
                        ('project_id', '=', self.add_line_project_id.id),
                        ('id', 'not in',
                         self.timesheet_ids.mapped('task_id').ids)],
                },
            }
        else:
            return {
                'domain': {
                    'add_line_task_id': [('id', '=', False)],
                },
            }
