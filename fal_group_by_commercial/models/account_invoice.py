# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('partner_id')
    def _get_parent_company(self):
        for invoice in self:
            invoice.fal_parent_company = invoice.partner_id.is_company and invoice.partner_id.fal_parent_company or invoice.partner_id.parent_id.fal_parent_company or False

    fal_parent_company = fields.Many2one(
        'res.partner',
        compute='_get_parent_company',
        string='Parent Company',
        help='The Parent Company for group',
        readonly=True,
        store=True
    )

# End of AccountInvoice()
