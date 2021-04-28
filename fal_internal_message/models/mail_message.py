from odoo import api, models


class Message(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def _notify_compute_recipients(self, record, msg_vals):
        recipient_data = super(Message, self).\
            _notify_compute_recipients(record, msg_vals)
        if msg_vals['is_internal_message']:
            result = []
            for item in recipient_data['partners']:
                if self.env.ref('base.group_user').id in item['groups']:
                    result.append(item)
            recipient_data['partners'] = result
        return recipient_data
