# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_purchase_order_line_data(self, so_line, date_order, purchase_id, company):
        res = super(SaleOrder, self)._prepare_purchase_order_line_data(so_line, date_order, purchase_id, company)
        if not self.env.ref('analytic.analytic_comp_rule').active:
            if self.analytic_account_id:
                if self.analytic_account_id.company_id:
                    message = _("""
                        <p style=\"color:green\">Info:</p>
                        <ul>
                            <li>Analytic account is not global, it will not included to PO</li>
                        </ul>
                        """)
                    self.message_post(
                        subject=_("Info"),
                        body=message,
                    )
                else:
                    res['account_analytic_id'] = self.analytic_account_id.id
        return res
