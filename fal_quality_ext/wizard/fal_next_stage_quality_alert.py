from odoo import models, api


class FalNextStageQualityAlert(models.TransientModel):
    _name = 'fal.next.stage.quality.alert'

    @api.multi
    def button_next_stage_quality_alert(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        source = self.env['quality.alert'].browse(active_ids)
        source.next_stage_quality_alert()
