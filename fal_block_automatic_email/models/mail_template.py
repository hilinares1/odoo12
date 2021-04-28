# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MailTemplate(models.Model):
    _inherit = "mail.template"

    fal_can_send = fields.Boolean("Can send?", default=False)
    fal_allow_external_message = fields.Boolean(
        string="Allow External Message",
        default=True
    )

    @api.multi
    def send_mail(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
        res = False
        if self.fal_can_send:
            res = super(MailTemplate, self).send_mail(res_id, force_send, raise_exception, email_values, notif_layout)
        return res

    @api.multi
    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can ben generated
        instead of the template values if requested by template or context.
        Emails (email_to, email_cc) can be transformed into partners if requested
        in the context. """
        self.ensure_one()
        results = super(MailTemplate, self).generate_recipients(results, res_ids)
        if self.fal_allow_external_message:
            return results
        else:
            partner_ids = []
            for result in results:
                for partner_id in results[result]['partner_ids']:
                    partner_id = self.env['res.partner'].browse(partner_id)
                    partner_user_ids = partner_id.user_ids
                    for partner_user_id in partner_user_ids:
                        if partner_user_id.user_has_groups('base.group_user'):
                            partner_ids.append(partner_id.id)
            results[result]['partner_ids'] = partner_ids
            return results

# End of MailTemplate()


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self, auto_commit=False):
        res = False
        if self.template_id:
            if self.template_id.fal_can_send:
                res = super(MailComposer, self).send_mail(auto_commit=auto_commit)
        else:
            res = super(MailComposer, self).send_mail(auto_commit=auto_commit)
        return res

# End of MailComposer()
