from odoo import models, fields, _


class FalLostQuotation(models.TransientModel):
    _name = 'fal.cancel.quotation.wizard'

    fal_cancel_reason = fields.Many2one(
        'fal.cancel.reason', string='Cancel Reason')
    notes = fields.Text(string='Notes')

    def action_confirm_cancel(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        sale_ids = self.env['sale.order'].browse(active_id)
        current_user_id = self._uid
        res_uid = self.env['res.users'].browse(current_user_id)
        message = _("Cancel Reason: %s <p>Notes: %s</p>") % (
            self.fal_cancel_reason.name, self.notes)
        message_id = sale_ids.message_post(body=message)
        message_id.write({'author_id': res_uid.partner_id.id})
        sale_ids.action_cancel()
