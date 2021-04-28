from odoo import api, models, fields, _
from odoo.exceptions import UserError


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    fal_short_description = fields.Char('Short Description')
    fal_kanban_state = fields.Selection([
        ('normal', 'Normal'),
        ('blocked', 'Blocked'),
        ('done', 'Ready for next stage')], string='Containment',
        default='normal', required=True,
        track_visibility='onchange', copy=False)
    fal_last_stage = fields.Boolean(compute='_fal_is_last_stage')
    fal_first_stage = fields.Boolean(compute='_fal_is_last_stage')

    @api.depends('stage_id', 'stage_id.sequence')
    def _fal_is_last_stage(self):
        alert_stage = self.env['quality.alert.stage']
        for quality in self:
            first_stages = alert_stage.search([], limit=1, order='sequence asc')
            last_stages = alert_stage.search([], limit=1, order='sequence desc')
            if quality.stage_id.sequence != 0:
                if quality.stage_id.sequence == last_stages.sequence:
                    quality.fal_last_stage = True
            if quality.stage_id.sequence == first_stages.sequence:
               quality.fal_first_stage = True

    @api.multi
    def action_next_stage_quality_alert(self):
        return {
            'name': 'Move to Next Stage',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.next.stage.quality.alert',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def next_stage_quality_alert(self):
        alert_stage = self.env['quality.alert.stage']
        all_stages = alert_stage.search([])
        for quality in self:
            if len(all_stages) == len(all_stages.filtered(lambda a: a.sequence == 0)):
                raise UserError(_('Please Set sequence on Quality Alert Stage'))
            next_stage_ids = alert_stage.search(
                [('sequence', '>', quality.stage_id.sequence)], limit=1).id
            if next_stage_ids:
                quality.write({
                    'stage_id': next_stage_ids,
                })

    @api.multi
    def action_reset(self):
        alert_stage = self.env['quality.alert.stage']
        for quality in self:
            first_stages = alert_stage.search([], limit=1, order='sequence asc')
            if first_stages:
                quality.write({
                    'stage_id': first_stages.id,
                })


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    @api.multi
    def do_pass(self):
        for quality_check in self:
            for alert in quality_check.alert_ids:
                if not alert.stage_id.done:
                    raise UserError(_('Cannot pass the product,\
                        because %s is not Done.') % (alert.name))
        return super(QualityCheck, self).do_pass()
