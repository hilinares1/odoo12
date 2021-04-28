# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.one
    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        res = super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        if not self.env.ref('analytic.analytic_comp_rule').active:
            if self.order_line and self.order_line[0].account_analytic_id:
                if self.order_line[0].account_analytic_id.company_id:
                    message = _("""
                        <p style=\"color:green\">Info:</p>
                        <ul>
                            <li>Analytic account is not global, it will not included to SO</li>
                        </ul>
                        """)
                    self.message_post(
                        subject=_("Info"),
                        body=message,
                    )
                else:
                    res[0]['analytic_account_id'] = self.order_line[0].account_analytic_id.id
        # return res[0], because every make a super on this function, always return a list.
        return res[0]
