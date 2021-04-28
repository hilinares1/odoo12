from odoo import api, fields, models


class MailTemplate(models.AbstractModel):
    _inherit = 'mail.template'

    def _get_default_allow_external_message(self):
        if self.model_id:
            return self.model_id.fal_allow_external_message
        else:
            return True

    fal_allow_external_message = fields.Boolean(
        string="Allow External Message",
        default=_get_default_allow_external_message
    )

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.fal_allow_external_message = self.model_id.fal_allow_external_message
