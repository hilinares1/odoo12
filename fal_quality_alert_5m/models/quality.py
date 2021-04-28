from odoo import models, fields, api
from odoo.http import request


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    fal_qa_5m_count = fields.Integer(
        'Count Quality Alerts 5M',
        compute="_compute_fal_qa_5m_count")

    @api.multi
    def _compute_fal_qa_5m_count(self):
        for alert in self:
            alert_count = self.env['fal.qa.5m'].search(
                [('quality_alert_id', '=', self.ids)])
            alert.fal_qa_5m_count = len(alert_count)

    fal_qa_5m_id = fields.Many2one(
        'fal.qa.5m', string='Quality Alerts 5M ID')

    @api.multi
    def action_create_fal_qa_5m(self):
        fal_qa_5m_id = request.env['fal.qa.5m'].create({
            'quality_alert_id': self.id,
            'short_description': self.fal_short_description,
        })
        view_id = self.env.ref('fal_quality_alert_5m.view_fal_qa_5m_form').id
        context = self._context.copy()
        return {
            'name': 'fal.qa.5m.form',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'fal.qa.5m',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': fal_qa_5m_id.id,
            'target': 'current',
            'context': context,
        }

    @api.multi
    def action_open_alert_5m(self):
        self.ensure_one()
        action = self.env.ref('fal_quality_alert_5m.action_fal_qa_5m')
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
