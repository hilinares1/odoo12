# -*- coding: utf-8 -*-
from odoo import models, api, fields
# from odoo.exceptions import UserError, Warning
import logging
_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        """ Track updated values. Comparing the initial and current values of
        the fields given in tracked_fields, it generates a message containing
        the updated values. This message can be linked to a
        mail.message.subtype
        given by the ``_track_subtype`` method. """
        if not tracked_fields:
            return True

        tracking = self._message_track_get_changes(
            tracked_fields, initial_values)
        for record in self:
            changes, tracking_value_ids = tracking[record.id]
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtype_xmlid = False
            # By passing this key, that allows to let the subtype empty and
            # so don't sent email because partners_to_notify from mail_message
            # s._notify will be empty
            if not self._context.get('mail_track_log_only'):
                subtype_xmlid = record._track_subtype(dict((
                    col_name, initial_values[record.id][col_name]
                ) for col_name in changes))

            if subtype_xmlid:
                subtype_rec = self.env.ref(
                    subtype_xmlid)  # TDE FIXME check for raise if not found
                if not (subtype_rec and subtype_rec.exists()):
                    _logger.debug('subtype %s not found' % subtype_xmlid)
                    continue

                # overide method
                body = ''
                subject = ''
                if subtype_rec and subtype_rec.fal_template_id:
                    body = self.env['mail.template']._render_template(
                        subtype_rec.fal_template_id.body_html,
                        subtype_rec.res_model, [record.id])
                    subject = self.env['mail.template']._render_template(
                        subtype_rec.fal_template_id.subject,
                        subtype_rec.res_model, [record.id])
                    if body:
                        body = body[record.id]
                    if subject:
                        subject = subject[record.id]
                if subtype_rec and subtype_rec.fal_is_track_value:
                    record.message_post(
                        subtype=subtype_xmlid,
                        subject=subject,
                        tracking_value_ids=tracking_value_ids,
                        body=body)
                else:
                    record.message_post(
                        subtype=subtype_xmlid,
                        subject=subject,
                        body=body)
                # =============================
            elif tracking_value_ids:
                record._message_log(tracking_value_ids=tracking_value_ids)

        self._message_track_post_template(tracking)

        return True


class MailMessageSubtype(models.Model):
    _inherit = 'mail.message.subtype'

    fal_template_id = fields.Many2one(
        'mail.template', 'Email Template',
    )
    fal_is_track_value = fields.Boolean('Is track value?', default=True)
