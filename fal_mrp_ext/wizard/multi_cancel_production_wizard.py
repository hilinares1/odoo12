from odoo import models, api, _
from odoo.exceptions import UserError


class MultiCancelProductionWizard(models.TransientModel):
    _name = "multi.cancel.production.wizard"

    @api.multi
    def action_cancel(self):
        context = dict(self._context)
        mrp_ids = self.env['mrp.production'].browse(context.get('active_ids'))
        for mrp_id in mrp_ids:
            if mrp_id.state == 'done':
                raise UserError(_("You cannot cancel a production order that has been set to 'Done'"))
            else:
                mrp_id.action_cancel()
