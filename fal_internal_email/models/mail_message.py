from odoo import api, fields, models


class Message(models.Model):
    _inherit = 'mail.message'

    fal_allow_external_message = fields.Boolean(
        string="Allow External Message",
        default=True
    )

    @api.multi
    def _notify_compute_recipients(self, record, msg_vals):
        recipient_data = super(Message, self).\
            _notify_compute_recipients(record, msg_vals)
        if record:
            # Block external in record
            if not self.env[msg_vals['model']].browse(msg_vals['res_id']).fal_allow_external_message:
                result = []
                for item in recipient_data['partners']:
                    if self.env.ref('base.group_user').id in item['groups']:
                        result.append(item)
                recipient_data['partners'] = result
            else:
                #Block external in email template
                if not msg_vals['fal_allow_external_message']:
                    result = []
                    for item in recipient_data['partners']:
                        if self.env.ref('base.group_user').id in item['groups']:
                            result.append(item)
                    recipient_data['partners'] = result
        return recipient_data
