from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CustomInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_draft_number = fields.Char(
        'Draft Number', copy=False, default='New'
    )

    @api.model
    def create(self, vals):
        if vals.get('fal_draft_number', 'New') == 'New':
            if self._context.get('type') == 'in_invoice' or \
                    vals.get('type') == 'in_invoice':
                vals['fal_draft_number'] = self.env['ir.sequence']\
                    .next_by_code('bill.number') or 'New'
            elif self._context.get('type') == 'out_invoice' or \
                    vals.get('type') == 'out_invoice':
                vals['fal_draft_number'] = self.env['ir.sequence']\
                    .next_by_code('draft.number') or 'New'
        return super(CustomInvoice, self).create(vals)
