# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fal_project_budget_line_id = fields.Many2one('fal.project.budget.line', "Control Line")

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['fal_project_budget_line_id'] = self.fal_project_budget_line_id and self.fal_project_budget_line_id.id
        return res

# end of SaleOrderLine()
