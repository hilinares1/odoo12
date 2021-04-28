# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, sql_db, _
from odoo.tools.mimetypes import guess_mimetype
from datetime import datetime
from odoo.exceptions import UserError
import html2text
import logging

_logger = logging.getLogger(__name__)

class WhatsappComposeMessage(models.TransientModel):
    _inherit = 'whatsapp.compose.message'
    
    purchase_ids = fields.Many2many('purchase.order', string='Purchase')
    
    @api.model
    def default_get(self, fields):
        result = super(WhatsappComposeMessage, self).default_get(fields)
        if self.env.context.get('active_model') and self.env.context.get('active_id'):
            active_model = self.env.context.get('active_model')
            res_id = self.env.context.get('active_id')
            res_ids = self.env.context.get('active_ids')
            rec = self.env[active_model].browse(res_id)
            result['subject'] = ''
            is_multi_order = False
            if active_model == 'purchase.order':
                result['purchase_ids'] = res_ids
                if len(res_ids) > 1:
                    template_id = self.env.ref('aos_whatsapp_purchase.purchase_validate_multi', raise_if_not_found=False)
                    result['attachment_ids'] = []
                    is_multi_order = True
                else:
                    if self.env.context.get('send_rfq', False):
                        template_id = self.env.ref('purchase.email_template_edi_purchase')
                    else:
                        template_id = self.env.ref('purchase.email_template_edi_purchase_done') 
            msg = result.get('message', '')
            if active_model == 'purchase.order':
                template = template_id.generate_email(rec.id)
                body = template.get('body')
                msg = html2text.html2text(body)
                if not is_multi_order:
                    result['template_id'] = template_id and template_id.id
                    result['subject'] = template_id and template_id.subject
                result['subject'] = result['subject'] or 'Purchase Confirmation'
            result['message'] = msg
        return result
    
                