# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action


class analytic_report(models.AbstractModel):
    _inherit = 'account.analytic.report'

    filter_ifrs = False

    def _get_balance_for_group(self, group, analytic_line_domain):
        analytic_line_domain_for_group = list(analytic_line_domain)
        if group:
            # take into account the hierarchy on account.analytic.line
            analytic_line_domain_for_group += [('group_id', 'child_of', group.id)]
        else:
            analytic_line_domain_for_group += [('group_id', '=', False)]

        currency_obj = self.env['res.currency']
        user_currency = self.env.user.company_id.currency_id
        analytic_lines = self.env['account.analytic.line'].read_group(analytic_line_domain_for_group, ['amount', 'fal_amount_group_curr', 'currency_id'], ['currency_id'])

        if self.env.context.get('ifrs', False):
            balance = sum([row['fal_amount_group_curr'] for row in analytic_lines])
        else:
            balance = sum([currency_obj.browse(row['currency_id'][0])._convert(
                row['amount'], user_currency, self.env.user.company_id, fields.Date.today()) for row in analytic_lines])
        return balance

    def _generate_analytic_account_lines(self, analytic_accounts, parent_id=False):
        lines = []

        for account in analytic_accounts:
            # Override Start
            # Call the fal_balance_group_curr instead of standard balance
            if self.env.context.get('ifrs', False):
                lines.append({
                    'id': 'analytic_account_%s' % account.id,
                    'name': account.name,
                    'columns': [{'name': account.code},
                                {'name': account.partner_id.display_name},
                                {'name': self.format_value(account.fal_balance_group_curr)}],
                    'level': 4,  # todo check redesign financial reports, should be level + 1 but doesn't look good
                    'unfoldable': False,
                    'caret_options': 'account.analytic.account',
                    'parent_id': parent_id,  # to make these fold when the original parent gets folded
                })
            else:
                lines.append({
                    'id': 'analytic_account_%s' % account.id,
                    'name': account.name,
                    'columns': [{'name': account.code},
                                {'name': account.partner_id.display_name},
                                {'name': self.format_value(account.balance)}],
                    'level': 4,  # todo check redesign financial reports, should be level + 1 but doesn't look good
                    'unfoldable': False,
                    'caret_options': 'account.analytic.account',
                    'parent_id': parent_id,  # to make these fold when the original parent gets folded
                })

        return lines
