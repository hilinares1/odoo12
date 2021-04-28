# -*- coding: utf-8 -*-

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_proposal(self):
        if super(SaleOrder, self)._check_proposal():
            return True
        else:
            if self.partner_id.state == 'qualified':
                return False
            else:
                return True
