from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class FalQualityAlert5Y(models.Model):
    _name = 'fal.qa.5y'
    _description = "Quality Alerts 5Y"

    # user will type manually, no need sequence
    name = fields.Char(string='Title', default='(Title)')

    short_description = fields.Char('Short Description')

    quality_alert_id = fields.Many2one(
        'quality.alert', string='Quality Alerts ID')

    date = fields.Date(
        string='Date', required=True,
        default=lambda self: self._context.get(
            'date', fields.Date.context_today(self)))

    # fields for 5Y table
    table_1a = fields.Text(string='First Why')
    table_2a = fields.Text(string='Second Why A')
    table_2b = fields.Text(string='Second Why B')
    table_2c = fields.Text(string='Second Why C')
    table_2d = fields.Text(string='Second Why D')
    table_2e = fields.Text(string='Second Why E')
    table_3a = fields.Text(string='Third Why A')
    table_3b = fields.Text(string='Third Why B')
    table_3c = fields.Text(string='Third Why C')
    table_3d = fields.Text(string='Third Why D')
    table_3e = fields.Text(string='Third Why E')
    table_4a = fields.Text(string='Fourth Why A')
    table_4b = fields.Text(string='Fourth Why B')
    table_4c = fields.Text(string='Fourth Why C')
    table_4d = fields.Text(string='Fourth Why D')
    table_4e = fields.Text(string='Fourth Why E')
    table_5a = fields.Text(string='Fifth Why A')
    table_5b = fields.Text(string='Fifth Why B')
    table_5c = fields.Text(string='Fifth Why C')
    table_5d = fields.Text(string='Fifth Why D')
    table_5e = fields.Text(string='Fifth Why E')

    @api.multi
    def action_see_alert(self):
        return {
            'name': _('Quality Alerts'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'quality.alert',
            'target': 'current',
            'res_id': self.quality_alert_id.id,
        }
