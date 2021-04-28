from odoo import models, api


class MultiCancelPickingWizard(models.TransientModel):
    _name = "multi.cancel.picking.wizard"

    @api.multi
    def action_cancel(self):
        context = dict(self._context)
        self.env['stock.picking'].browse(context.get('active_ids')).action_cancel()
