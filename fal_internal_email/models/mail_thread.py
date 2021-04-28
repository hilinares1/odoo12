from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    fal_allow_external_message = fields.Boolean(
        string="Allow External Message",
        default=True
    )

    @api.model
    def get_fal_allow_external(self, res):
        is_external_msg = True
        result = self.message_ids.search([
            ('res_id', '=', res['res_id']),
            ('model', '=', res['model'])
        ])
        for rec in result:
            is_external_msg = rec.fal_allow_external_message
        self.env[res['model']].browse(res['res_id']).fal_allow_external_message = is_external_msg
        return is_external_msg

    @api.model
    def fal_allow_external(self, res, value):
        result = self.message_ids.search([
            ('res_id', '=', res['res_id']),
            ('model', '=', res['model'])
        ])
        for rec in result:
            rec.fal_allow_external_message = value
        self.env[res['model']].browse(res['res_id']).fal_allow_external_message = value
        return value
