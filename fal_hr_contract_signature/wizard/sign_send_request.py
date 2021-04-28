# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'
    _description = 'Sign send request'

    @api.model
    def default_get(self, fields):
        res = super(SignSendRequest, self).default_get(fields)

        template_id = self.env.context.get('contract_template_id')
        if template_id:
            res['template_id'] = template_id
            template = self.env['sign.template'].browse(res['template_id'])
            res['filename'] = template.attachment_id.name
            res['subject'] = _("Signature Request - %s") % (template.attachment_id.name)

        return res
