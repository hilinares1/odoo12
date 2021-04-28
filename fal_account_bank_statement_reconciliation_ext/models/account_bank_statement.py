# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools import pycompat


class account_bank_statement_line(models.Model):
    _name = 'account.bank.statement.line'
    _inherit = 'account.bank.statement.line'

    product_id = fields.Many2one('product.product', 'Product')
    # merge from falinwa_field_ext
    ref = fields.Char('Reference', size=64)
    # merge end

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.description or self.product_id.name
            account_id = False
            if self.product_id.categ_id.property_account_general_id:
                account_id = self.product_id.categ_id.property_account_general_id or False
            if self.product_id.property_account_general_id:
                account_id = self.product_id.property_account_general_id or False
            self.account_id = account_id

# end of account_bank_statement_line()


class account_bank_statement(models.Model):
    _name = 'account.bank.statement'
    _inherit = 'account.bank.statement'

    fal_description = fields.Text('Description')
    fal_remark = fields.Text('Remark')
