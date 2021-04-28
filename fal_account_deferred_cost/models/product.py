# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    deferred_cost_category_id = fields.Many2one('account.asset.category', string='Deferred Cost Type', company_dependent=True, ondelete="restrict")

    @api.multi
    def _get_asset_accounts(self):
        res = super(ProductTemplate, self)._get_asset_accounts()
        if self.deferred_cost_category_id:
            res['stock_input'] = self.property_account_expense_id
        return res
