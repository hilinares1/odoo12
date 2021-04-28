# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        if self and self.partner_id and self.partner_id.state != 'qualified':
            raise UserError(_('This partner in not qualified, please ask \
                contact qualificator to qualified partner'))
        return res
