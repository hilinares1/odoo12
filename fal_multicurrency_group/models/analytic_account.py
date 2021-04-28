# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    fal_debit_group_curr = fields.Monetary(
        compute='_compute_debit_credit_group_balance',
        string='Debit IFRS',
        help="Debit in IFRS Currency.",
        currency_field='group_currency_id',
    )
    fal_credit_group_curr = fields.Monetary(
        compute='_compute_debit_credit_group_balance',
        string='Credit IFRS',
        help="Credit in IFRS Currency.",
        currency_field='group_currency_id',
    )
    fal_balance_group_curr = fields.Monetary(
        compute='_compute_debit_credit_group_balance',
        string='Balance IFRS',
        help="Balance in IFRS Currency.",
        currency_field='group_currency_id',
    )
    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )

    @api.multi
    def _compute_debit_credit_group_balance(self):
        Curr = self.env['res.currency']
        analytic_line_obj = self.env['account.analytic.line']
        domain = [('account_id', 'in', self.ids)]
        if self._context.get('from_date', False):
            domain.append(('date', '>=', self._context['from_date']))
        if self._context.get('to_date', False):
            domain.append(('date', '<=', self._context['to_date']))
        if self._context.get('tag_ids'):
            tag_domain = expression.OR([[('tag_ids', 'in', [tag])] for tag in self._context['tag_ids']])
            domain = expression.AND([domain, tag_domain])
        if self._context.get('company_ids'):
            domain.append(('company_id', 'in', self._context['company_ids']))

        credit_groups = analytic_line_obj.search(domain + [('amount', '>=', 0.0)])
        data_credit = defaultdict(float)
        for l in credit_groups:
            data_credit[l['account_id'][0].id] += l.fal_amount_group_curr

        debit_groups = analytic_line_obj.search(domain + [('amount', '<', 0.0)])
        data_debit = defaultdict(float)
        for l in debit_groups:
            data_debit[l['account_id'][0].id] += l.fal_amount_group_curr

        for account in self:
            account.fal_debit_group_curr = abs(data_debit.get(account.id, 0.0))
            account.fal_credit_group_curr = data_credit.get(account.id, 0.0)
            account.fal_balance_group_curr = account.fal_credit_group_curr - account.fal_debit_group_curr


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    fal_amount_group_curr = fields.Monetary(
        compute='_amount_all_to_group_curr',
        string='Balance Group',
        help="Balance in IFRS Currency.",
        store=True,
        currency_field='group_currency_id',
    )

    @api.depends('amount', 'currency_id', 'group_currency_id')
    def _amount_all_to_group_curr(self):
        cur_obj = self.env['res.currency']
        amount_total = 0.0
        for analytic_line in self:
            amount = 0.0
            # Define Self Currency
            self_currency = analytic_line.currency_id or analytic_line.company_id.currency_id
            curr_id = analytic_line.company_id.group_currency_id or self_currency

            for line in cur_obj.browse(curr_id):
                amount += abs(analytic_line.amount)
                if self_currency != curr_id:
                    currency_id = self_currency.with_context(date=analytic_line.date)
                    amount_total = currency_id._convert(
                        amount,
                        curr_id,
                        analytic_line.company_id,
                        analytic_line.date
                    )
                else:
                    amount_total = amount
            analytic_line.fal_amount_group_curr = amount_total
