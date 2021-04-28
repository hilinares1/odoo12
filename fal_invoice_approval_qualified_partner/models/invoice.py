# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError, Warning


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        if self and self.partner_id and self.partner_id.state != 'qualified':
            raise Warning(_('This partner in not qualified, please ask \
                contact qualificator to qualified partner'))
        return super(AccountInvoice, self).action_invoice_open()
