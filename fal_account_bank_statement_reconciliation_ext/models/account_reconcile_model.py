# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    # ===== Write-Off =====
    # First part fields.
    product_id = fields.Many2one('product.product', string='Product', ondelete='cascade')

    # Second part fields.
    second_product_id = fields.Many2one('product.product', string='Product', ondelete='cascade')
    
    ####################################################
    # RECONCILIATION PROCESS
    ####################################################

    @api.model
    def _get_taxes_move_lines_dict(self, tax, base_line_dict):
        ''' Get move.lines dict (to be passed to the create()) corresponding to a tax.
        :param tax:             An account.tax record.
        :param base_line_dict:  A dict representing the move.line containing the base amount.
        :return: A list of dict representing move.lines to be created corresponding to the tax.
        '''
        balance = base_line_dict['debit'] - base_line_dict['credit']
        currency = base_line_dict.get('currency_id') and self.env['res.currency'].browse(base_line_dict['currency_id'])

        res = tax.compute_all(balance, currency=currency)

        new_aml_dicts = []
        for tax_res in res['taxes']:
            tax = self.env['account.tax'].browse(tax_res['id'])

            new_aml_dicts.append({
                'account_id': tax.account_id and tax.account_id.id or base_line_dict['account_id'],
                'name': tax.name,
                'product_id': base_line_dict.get('product_id'),
                'partner_id': base_line_dict.get('partner_id'),
                'debit': tax_res['amount'] > 0 and tax_res['amount'] or 0,
                'credit': tax_res['amount'] < 0 and -tax_res['amount'] or 0,
                'analytic_account_id': tax.analytic and base_line_dict['analytic_account_id'],
                'analytic_tag_ids': tax.analytic and base_line_dict['analytic_tag_ids'],
                'tax_exigible': tax.tax_exigibility == 'on_payment',
            })

            # Handle price included taxes.
            base_line_dict['debit'] = tax_res['base'] > 0 and tax_res['base'] or base_line_dict['debit']
            base_line_dict['credit'] = tax_res['base'] < 0 and -tax_res['base'] or base_line_dict['credit']

        return new_aml_dicts

    @api.multi
    def _get_write_off_move_lines_dict(self, st_line, move_lines=None):
        ''' Get move.lines dict (to be passed to the create()) corresponding to the reconciliation model's write-off lines.
        :param st_line:     An account.bank.statement.line record.
        :param move_lines:  An account.move.line recordset.
        :return: A list of dict representing move.lines to be created corresponding to the write-off lines.
        '''
        self.ensure_one()

        if self.rule_type == 'invoice_matching' and (not self.match_total_amount or (self.match_total_amount_param == 100)):
            return []

        line_residual = st_line.currency_id and st_line.amount_currency or st_line.amount
        line_currency = st_line.currency_id or st_line.journal_id.currency_id or st_line.company_id.currency_id
        total_residual = move_lines and sum(aml.currency_id and aml.amount_residual_currency or aml.amount_residual for aml in move_lines) or 0.0

        balance = total_residual - line_residual

        if not self.account_id or float_is_zero(balance, precision_rounding=line_currency.rounding):
            return []

        if self.amount_type == 'percentage':
            line_balance = balance * (self.amount / 100.0)
        else:
            line_balance = self.amount * (1 if balance > 0.0 else -1)

        new_aml_dicts = []

        # First write-off line.
        writeoff_line = {
            'name': self.label or st_line.name,
            'product_id': self.product_id.id,
            'account_id': self.account_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'debit': line_balance > 0 and line_balance or 0,
            'credit': line_balance < 0 and -line_balance or 0,
        }
        new_aml_dicts.append(writeoff_line)

        if self.tax_id:
            writeoff_line['tax_ids'] = [(6, None, [self.tax_id.id])]
            tax = self.tax_id
            if self.force_tax_included:
                tax = tax.with_context(force_price_include=True)
            new_aml_dicts += self._get_taxes_move_lines_dict(tax, writeoff_line)

        # Second write-off line.
        if self.has_second_line and self.second_account_id:
            line_balance = balance - sum(aml['debit'] - aml['credit'] for aml in new_aml_dicts)
            second_writeoff_line = {
                'name': self.second_label or st_line.name,
                'account_id': self.second_account_id.id,
                'product_id': self.second_product_id.id,
                'analytic_account_id': self.second_analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, self.second_analytic_tag_ids.ids)],
                'debit': line_balance > 0 and line_balance or 0,
                'credit': line_balance < 0 and -line_balance or 0,
            }
            new_aml_dicts.append(second_writeoff_line)

            if self.second_tax_id:
                second_writeoff_line['tax_ids'] = [(6, None, [self.second_tax_id.id])]
                tax = self.second_tax_id
                if self.force_second_tax_included:
                    tax = tax.with_context(force_price_include=True)
                new_aml_dicts += self._get_taxes_move_lines_dict(tax, second_writeoff_line)

        return new_aml_dicts
