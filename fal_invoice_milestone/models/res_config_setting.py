from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_active_milestone_cron = fields.Boolean(
        string='Run milestone by scheduled actions', default=True
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        IrDefault = self.env['ir.default'].sudo()
        res.update(
            fal_active_milestone_cron=IrDefault.get('sale.order', 'fal_milestone_by_cron') or False
            )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('sale.order', 'fal_milestone_by_cron', self.fal_active_milestone_cron)
