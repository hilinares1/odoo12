# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import date
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    def action_view_project_dashboard(self):
        action = self.env.ref(
            'fal_project_dashboard.fal_project_dashboard').read()[0]
        action['params'] = {
            'project_ids': self.analytic_account_id.ids,
        }
        action['context'] = {
            'active_id': self.analytic_account_id.id,
            'active_ids': self.analytic_account_id.ids,
            'search_default_display_name': self.analytic_account_id.name,
        }
        return action


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    fal_turnover = fields.Float(string="Turnover", compute='_get_turnover_amount')
    fal_variable_cost_margin = fields.Float(string="Variable Cost Margin", compute='_get_turnover_amount')
    fal_gross_value = fields.Float(string="Gross Value", compute='_get_turnover_amount')
    fal_net_value = fields.Float(string="Net Value", compute='_get_turnover_amount')

    @api.one
    def _get_turnover_amount(self):
        timesheet_amount = self._prepare_move_search('timesheet', options=None)
        expense_amount = self._prepare_move_search('mission', options=None)
        self.fal_turnover = self._prepare_order_search('saleinv', options=None)['fal_total']
        self.fal_variable_cost_margin = self._prepare_order_search('purcinv', options=None)['fal_total']
        self.fal_gross_value = self.fal_turnover - self.fal_variable_cost_margin
        self.fal_net_value = self.fal_gross_value - timesheet_amount['fal_total'] - expense_amount['fal_total']

    summary = fields.Char()

    def create_note(self, vals):
        summary = vals.get('summary', False)
        self.write({'summary': summary})
        if summary:
            self.message_post(body=vals.get('summary'))

    def action_view_project_dashboard(self):
        action = self.env.ref(
            'fal_project_dashboard.fal_project_dashboard').read()[0]
        action['params'] = {
            'project_ids': self.ids,
        }
        action['context'] = {
            'active_id': self.id,
            'active_ids': self.ids,
            'search_default_display_name': self.name,
        }
        return action

    @api.multi
    def get_total_due(self, tag, options):
        MoveLine = self.env['account.move.line']
        today = fields.date.today()
        for analytic_account in self:
            searchtemp = [
                ('analytic_account_id', 'child_of', analytic_account.ids),
                ('invoice_id.state', 'in', ['open']),
                ('invoice_id.type', 'in', ['out_invoice', 'out_refund']),
                ('reconciled', '=', False),
            ]
            if tag == 'notdue':
                searchtemp.append(('date_maturity', '!=', False))
                searchtemp.append(('date_maturity', '>', today))
            elif tag == '30d':
                searchtemp.append(('date_maturity', '!=', False))
                searchtemp.append(('date_maturity', '<=', today))
                searchtemp.append(('date_maturity', '>=', today - relativedelta(days=30)))
            elif tag == '60d':
                searchtemp.append(('date_maturity', '!=', False))
                searchtemp.append(('date_maturity', '<=', today - relativedelta(days=30)))
                searchtemp.append(('date_maturity', '>=', today - relativedelta(days=60)))
            elif tag == '61d':
                searchtemp.append(('date_maturity', '!=', False))
                searchtemp.append(('date_maturity', '<=', today - relativedelta(days=61)))

            if options and options['date']['date_from'] and options['date']['date_to']:
                searchtemp.append(
                    ('invoice_id.date_invoice', '>=', options['date']['date_from'])
                )
                searchtemp.append(
                    ('invoice_id.date_invoice', '<=', options['date']['date_to']),
                )
            move_line_ids = MoveLine.search(searchtemp)
            amount_total = 0
            for move_line in move_line_ids:
                add_amount = ((move_line.balance - move_line.balance_cash_basis) * -1)
                amount_total += add_amount
            # convert from company currency to ifrs
            if options and options['option_value'] == 'ifrs_currency':
                company_curr = self.env.user.company_id.currency_id
                group_curr = self.env.user.company_id.group_currency_id
                amount_total = company_curr._convert(amount_total, group_curr, self.env.user.company_id, fields.Date.today())
            return amount_total

    def _prepare_order_search(self, tag, options):
        """
        tag :
        sale
        purchase
        saleinv
        purcinv
        """
        if tag == 'sale':
            DataOrder = self.env['sale.order']
            searchtemp = \
                [
                    ('analytic_account_id', 'child_of', self.ids),
                    ('state', 'in', ['sale', 'done']),
                ]
            if options and options['date']['date_from'] and options['date']['date_to']:
                searchtemp.append(
                    ('confirmation_date', '>=', options['date']['date_from'])
                )
                searchtemp.append(
                    ('confirmation_date', '<=', options['date']['date_to']),
                )
        elif tag == 'purchase':
            DataOrder = self.env['purchase.order.line']
            searchtemp = \
                [
                    ('account_analytic_id', 'child_of', self.ids),
                    ('order_id.state', 'in', ['purchase', 'done']),
                ]
            if options and options['date']['date_from'] and options['date']['date_to']:
                searchtemp.append(
                    ('date_planned', '>=', options['date']['date_from'])
                )
                searchtemp.append(
                    ('date_planned', '<=', options['date']['date_to']),
                )
        elif tag in ['saleinv', 'purcinv']:
            DataOrder = self.env['account.move.line']
            searchtemp = \
                [
                    ('analytic_account_id', 'child_of', self.ids),
                    ('invoice_id.state', 'in', ['open', 'paid']),
                ]
            if options and options['date']['date_from'] and options['date']['date_to']:
                searchtemp.append(
                    ('invoice_id.date_invoice', '>=', options['date']['date_from'])
                )
                searchtemp.append(
                    ('invoice_id.date_invoice', '<=', options['date']['date_to']),
                )
            if tag == 'saleinv':
                searchtemp.append(('invoice_id.type', 'in', ['out_invoice', 'out_refund']))
            elif tag == 'purcinv':
                searchtemp.append(('invoice_id.type', 'in', ['in_invoice', 'in_refund']))
        data_ids = DataOrder.search(searchtemp)
        amount_total = 0

        for line in data_ids:

            if tag == 'sale':
                add_amount = line.amount_untaxed
            elif tag == 'purchase':
                add_amount = line.price_subtotal
            elif tag in ['saleinv', 'purcinv']:
                if tag == 'saleinv':
                    add_amount = line.balance * -1
                elif tag == 'purcinv':
                    add_amount = line.balance

            if line.currency_id:
                curr = line.currency_id
            else:
                curr = line.company_id.currency_id
            current_curr = curr
            company_curr = self.env.user.company_id.currency_id
            if tag in ['sale', 'purchase']:
                if current_curr.id != company_curr.id:
                    add_amount = current_curr.compute(add_amount, company_curr)
            amount_total += add_amount
        if options and options['option_value'] == 'ifrs_currency':
            company_curr = self.env.user.company_id.currency_id
            group_curr = self.env.user.company_id.group_currency_id
            amount_total = company_curr._convert(amount_total, group_curr, self.env.user.company_id, fields.Date.today())
        if tag == 'sale':
            return {'fal_total': amount_total,
                    'fal_count': len(data_ids)}
        if tag in ['purchase', 'saleinv', 'purcinv']:
            if tag == 'purchase':
                data_map_ids = data_ids.mapped('order_id')
            elif tag in ['saleinv', 'purcinv']:
                data_map_ids = data_ids.mapped('invoice_id')
            return {'fal_total': amount_total,
                    'fal_count': len(data_map_ids)}

    def _prepare_move_search(self, tag, options):
        """
        tag :
        customer
        supplier
        timesheet
        mission
        """
        MoveLine = self.env['account.move.line']
        match_payment_ids = self.env['account.partial.reconcile']
        searchtemp = [('analytic_account_id', 'child_of', self.ids)]
        if tag in ['customer', 'supplier']:
            searchtemp.append(('invoice_id.state', 'in', ['open', 'paid']))
            if tag == 'customer':
                searchtemp.append(('invoice_id.type', 'in', ['out_invoice', 'out_refund']))
            elif tag == 'supplier':
                searchtemp.append(('invoice_id.type', 'in', ['in_invoice', 'in_refund']))
        elif tag in ['timesheet', 'mission']:
            if tag == 'timesheet':
                journal_id = self.env['account.journal'].search(
                    [('fal_is_timesheet_journal', '=', True)])
            elif tag == 'mission':
                journal_id = self.env['account.journal'].search(
                    [('fal_is_mission_expense_journal', '=', True)])
            searchtemp.append(('journal_id', 'in', journal_id.ids))
        move_line_ids = MoveLine.search(searchtemp)
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('move_id.date', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('move_id.date', '<=', options['date']['date_to']),
            )
        move_line_ids = MoveLine.search(searchtemp)
        amount_total = 0
        for line in move_line_ids:
            if tag in ['customer', 'supplier']:
                if tag == 'customer':
                    add_amount = line.balance_cash_basis * -1
                elif tag == 'supplier':
                    add_amount = line.balance_cash_basis
            elif tag in ['timesheet', 'mission']:
                add_amount = line.balance
            amount_total += add_amount
        for move in move_line_ids.mapped('move_id'):
            for move_line in move.line_ids:
                debit = move_line.matched_debit_ids
                credit = move_line.matched_credit_ids
                match_payment_ids += debit + credit
        if options and options['option_value'] == 'ifrs_currency':
            company_curr = self.env.user.company_id.currency_id
            group_curr = self.env.user.company_id.group_currency_id
            amount_total = company_curr._convert(amount_total, group_curr, self.env.user.company_id, fields.Date.today())
        return {'fal_total': amount_total,
                'fal_count': len(match_payment_ids)}

    def _prepare_timesheet_cost_count_search(self, options):
        AnalyticLines = self.env['account.analytic.line']
        searchtemp = \
            [
                ('account_id', 'child_of', self.ids),
                ('is_timesheet', '=', True),
            ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('date', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('date', '<=', options['date']['date_to']),
            )
        analytic_line_ids = AnalyticLines.search(searchtemp)
        total_hr = 0
        for line in analytic_line_ids:
            total_hr += line.unit_amount
        return {'fal_timesheet_cost_count': len(analytic_line_ids),
                'fal_timesheet_cost_total_hour': total_hr,
                }

    def _prepare_mission_expense_count_search(self, options):
        Expenses = self.env['hr.expense']
        searchtemp = \
            [
                ('analytic_account_id', 'child_of', self.ids),
                ('state', 'in', ['post', 'done']),
            ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('date', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('date', '<=', options['date']['date_to']),
            )
        expense_ids = Expenses.search(searchtemp)
        return {'fal_mission_expense_count': len(expense_ids)}

    def _prepare_budget_search(self, tag, options):
        """
        tag :
        sale
        purchase
        mission
        employee
        """
        data_obj = self.env['ir.model.data']
        ProjectBudget = self.env['fal.project.budget']
        mdl = 'fal_project_budget'
        if tag == 'sale':
            oid = 'fal_project_budget_tags_sales'
            res_id = '.'.join([mdl, oid])
        elif tag == 'purchase':
            oid = 'fal_project_budget_tags_purchases'
            res_id = '.'.join([mdl, oid])
        elif tag == 'mission':
            oid = 'fal_project_budget_tags_mission_expenses'
            res_id = '.'.join([mdl, oid])
        elif tag == 'employee':
            oid = 'fal_project_budget_tags_employee_timesheets'
            res_id = '.'.join([mdl, oid])
        tag_id = data_obj.xmlid_to_res_id(res_id)
        project_type = ProjectBudget.search([
            ('project_id', '=', self.id)], limit=1)
        searchtemp = \
            [
                ('project_id', 'child_of', self.ids),
                ('fal_budget_tags_ids', 'in', [tag_id]),
                ('type', '=', project_type.type),
                ('active', '=', True),
                ('state', 'not in', ['draft', 'cancel']),
            ]

        project_budget_ids = ProjectBudget.search(searchtemp)
        total_qty = 0
        amount_total = 0
        for project_budget_id in project_budget_ids:
            searchline = [
                ('fal_budget_tags_ids', 'in', [tag_id]),
                ('fal_project_budget_id.state', 'not in', ['done', 'cancel']),
                ('fal_project_budget_id.active', '=', True),
                ('project_id', 'child_of', self.id)
            ]
            if options and options['date']['date_from'] and options['date']['date_to']:
                searchline.append(
                    ('date_from', '>=', options['date']['date_from'])
                )
                searchline.append(
                    ('date_to', '<=', options['date']['date_to']),
                )
            line_ids = project_budget_id.fal_project_budget_line_ids.search(
                searchline)
            for line in line_ids:
                add_amount = line.t0_planned_amount
                add_total = line.product_qty
                current_curr = line.currency_id
                company_curr = self.env.user.company_id.currency_id
                if current_curr.id != company_curr.id:
                    add_amount = current_curr.compute(add_amount, company_curr)
                amount_total += add_amount
                total_qty += add_total
        if options and options['option_value'] == 'ifrs_currency':
            company_curr = self.env.user.company_id.currency_id
            group_curr = self.env.user.company_id.group_currency_id
            amount_total = company_curr._convert(amount_total, group_curr, self.env.user.company_id, fields.Date.today())
        return {'fal_total': amount_total,
                'fal_qty': total_qty}

    def _prepare_termination_search(self, tag, options):
        """
        tag :
        purchase
        employee
        mission
        """
        data_obj = self.env['ir.model.data']
        ProjectBudget = self.env['fal.project.budget']
        mdl = 'fal_project_budget'
        if tag == 'purchase':
            oid = 'fal_project_budget_tags_purchases'
            res_id = '.'.join([mdl, oid])
        elif tag == 'employee':
            oid = 'fal_project_budget_tags_employee_timesheets'
            res_id = '.'.join([mdl, oid])
        elif tag == 'mission':
            oid = 'fal_project_budget_tags_mission_expenses'
            res_id = '.'.join([mdl, oid])
        tag_id = data_obj.xmlid_to_res_id(res_id)

        searchtemp = \
            [
                ('project_id', 'child_of', self.id),
                ('state', '=', 'validate'),
            ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('date_from', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('date_to', '<=', options['date']['date_to']),
            )
        project_budget_ids = ProjectBudget.search(searchtemp)

        amt = 0  # amount total
        tqty = 0  # total quantity
        company_curr = self.env.user.company_id.currency_id
        for budget_id in project_budget_ids:
            for budget_line_id in budget_id.fal_project_budget_line_ids:
                has_correct_tag = False
                for budget_line_tag in budget_line_id.fal_budget_tags_ids:
                    if budget_line_tag.id == tag_id:
                        has_correct_tag = True
                if has_correct_tag:
                    add_amt = budget_line_id.t0_planned_amount
                    add_tqty = budget_line_id.product_qty
                    current_curr = budget_line_id.company_id.currency_id
                    if current_curr.id != company_curr.id:
                        add_amt = current_curr.compute(add_amt, company_curr)
                    amt += add_amt
                    tqty += add_tqty
        if options and options['option_value'] == 'ifrs_currency':
            group_curr = self.env.user.company_id.group_currency_id
            amt = company_curr._convert(amt, group_curr, self.env.user.company_id, fields.Date.today())
        return {'fal_total': amt,
                'fal_qty': tqty}


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fal_is_timesheet_journal = fields.Boolean('Is Timesheet Journal')
    fal_is_mission_expense_journal = fields.Boolean(
        'Is Mission Expense Journal')
