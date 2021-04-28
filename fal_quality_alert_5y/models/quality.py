from odoo import models, fields, api
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    fal_qa_5y_count = fields.Integer(
        'Count Quality Alerts 5Y',
        compute="_compute_fal_qa_5y_count")

    @api.multi
    def _compute_fal_qa_5y_count(self):
        for alert in self:
            alert_count = self.env['fal.qa.5y'].search(
                [('quality_alert_id', '=', self.ids)])
            alert.fal_qa_5y_count = len(alert_count)

    fal_qa_5y_id = fields.Many2one(
        'fal.qa.5y', string='Quality Alerts 5Y ID')

    @api.multi
    def action_create_fal_qa_5y(self):
        fal_qa_5y_id = request.env['fal.qa.5y'].create({
            'quality_alert_id': self.id,
            'short_description': self.fal_short_description,
        })
        view_id = self.env.ref('fal_quality_alert_5y.view_fal_qa_5y_form').id
        context = self._context.copy()
        return {
            'name': 'fal.qa.5y.form',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'fal.qa.5y',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': fal_qa_5y_id.id,
            'target': 'current',
            'context': context,
        }

    @api.multi
    def action_open_alert_5y(self):
        self.ensure_one()
        action = self.env.ref('fal_quality_alert_5y.action_fal_qa_5y')
        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': action.domain,
            'context': {'search_default_quality_alert_id': [self.id]}
        }
