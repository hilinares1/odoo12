# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.partner_id:
            self.account_analytic_id = self.partner_id.fal_project_id.id
        if self.product_id:
            self.account_analytic_id = self.product_id.fal_project_id.id
        return res


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(AccountBankStatementLine, self).onchange_product_id()
        if self.product_id:
            self.analytic_account_id = self.product_id.fal_project_id.id
        return res

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.analytic_account_id = self.partner_id.fal_project_id.id
