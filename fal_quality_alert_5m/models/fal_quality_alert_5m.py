from odoo import models, fields, api, _


class FalQualityAlert5M(models.Model):
    _name = 'fal.qa.5m'
    _description = "Quality Alerts 5M"

    # user will type manually, no need sequence
    name = fields.Char(string='Title', default='(Title)')
    short_description = fields.Char('Short Description')
    date = fields.Date(
        string='Date', required=True,
        default=lambda self: self._context.get(
            'date', fields.Date.context_today(self)))

    fal_qa_5m_mother_nature_ids = fields.One2many(
        'fal.qa.5m.line', 'fal_qa_5m_id',
        domain=[('fal_type', '=', 'mother_nature')],
        string="Mother Nature")
    fal_qa_5m_man_ids = fields.One2many(
        'fal.qa.5m.line', 'fal_qa_5m_id',
        domain=[('fal_type', '=', 'man')],
        string="Man")
    fal_qa_5m_material_ids = fields.One2many(
        'fal.qa.5m.line', 'fal_qa_5m_id',
        domain=[('fal_type', '=', 'material')],
        string="Material")
    fal_qa_5m_machine_ids = fields.One2many(
        'fal.qa.5m.line', 'fal_qa_5m_id',
        domain=[('fal_type', '=', 'machine')],
        string="Machine")
    fal_qa_5m_method_ids = fields.One2many(
        'fal.qa.5m.line', 'fal_qa_5m_id',
        domain=[('fal_type', '=', 'method')],
        string="Method")
    quality_alert_id = fields.Many2one(
        'quality.alert', string='Quality Alerts ID')

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


class FalQualityAlert5MType(models.Model):
    _name = 'fal.qa.5m.line'
    _description = "Quality Alerts 5M Type"

    fal_qa_5m_id = fields.Many2one(
        'fal.qa.5m', string='Quality Alert 5M')
    number = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5')],
        string='5M # Number')
    description = fields.Text(string='Comment')
    fal_type = fields.Selection([
        ('mother_nature', 'Mother Nature'),
        ('man', 'Man'),
        ('material', 'Material'),
        ('machine', 'Machine'),
        ('method', 'Method'),
    ])
