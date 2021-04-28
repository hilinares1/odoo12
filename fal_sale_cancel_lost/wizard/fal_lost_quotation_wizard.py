from odoo import models, fields, _


class FalLostQuotation(models.TransientModel):
    _name = 'fal.lost.quotation.wizard'

    fal_lost_reason = fields.Many2one('fal.lost.reason', string='Lost Reason')
    notes = fields.Text(string='Notes')

    def action_confirm_lost(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        sale_ids = self.env['sale.order'].browse(active_id)
        current_user_id = self._uid
        res_uid = self.env['res.users'].browse(current_user_id)
        message = _("Lost Reason: %s <p>Notes: %s</p>") % (
            self.fal_lost_reason.name, self.notes)
        message_id = sale_ids.message_post(body=message)
        message_id.write({'author_id': res_uid.partner_id.id})
        sale_ids.write({'state': 'lost'})
