# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    fal_project_budget_line_id = fields.Many2one('fal.project.budget.line', "Control Line")

# end of PurchaseOrderLine()
