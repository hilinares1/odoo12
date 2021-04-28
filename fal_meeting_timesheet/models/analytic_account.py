from odoo import models, fields


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    meeting_id = fields.Many2one(
        'calendar.event',
        string='Meeting')
