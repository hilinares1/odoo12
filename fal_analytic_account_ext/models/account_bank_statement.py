# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(
            self, counterpart_aml_dicts=None,
            payment_aml_rec=None, new_aml_dicts=None):
        res = super(AccountBankStatementLine, self).process_reconciliation(
            counterpart_aml_dicts, payment_aml_rec, new_aml_dicts)
        for line in self:
            for journal_entry in line.journal_entry_ids:
                journal_entry.write(
                    {'analytic_account_id': line.analytic_account_id.id})
        return res
