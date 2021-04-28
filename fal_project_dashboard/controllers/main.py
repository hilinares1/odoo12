# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat, config, date_utils
from odoo.tools.misc import formatLang, format_date, get_user_companies
from odoo import models, fields, api, _
from babel.dates import get_quarter_names
import logging
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
# round up
from math import ceil, floor
_logger = logging.getLogger(__name__)


class FalDashboardController(http.Controller):

    @http.route('/fal/dashboard', type='json', auth="user")
    def plan(self, domain, options):
        projects = request.env['account.analytic.account'].search(domain)
        self._apply_date_filter(options)
        values = self._plan_prepare_values(projects, options)
        view = request.env.ref('fal_project_dashboard.fal_dashboard')
        searchview_dict = {'options': options}
        return {
            'html_content': view.render(values),
            'project_ids': projects.ids,
            'searchview_html': request.env['ir.ui.view'].render_template(
                self._get_templates().get(
                    'search_template',
                    'fal_project_dashboard.search_template'
                ), values=searchview_dict),
            'searchview_options': options,
        }

    def _get_templates(self):
        return {
            'search_template': 'fal_project_dashboard.search_template',
        }

    def has_single_date_filter(self, options):
        return options['date'].get('date_from') is None

    def _apply_date_filter(self, options):
        def create_vals(period_vals):
            vals = {'string': period_vals['string']}
            if self.has_single_date_filter(options):
                vals['date'] = (
                    period_vals['date_to'] or period_vals['date_from']
                ).strftime(DEFAULT_SERVER_DATE_FORMAT)
            else:
                vals['date_from'] = period_vals['date_from'].strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
                vals['date_to'] = period_vals['date_to'].strftime(
                    DEFAULT_SERVER_DATE_FORMAT)
            return vals

        # ===== Date Filter =====
        if not options.get('date') or not options['date'].get('filter'):
            return
        options_filter = options['date']['filter']

        date_from = None
        date_to = datetime.date.today()
        if options_filter == 'custom':
            if self.has_single_date_filter(options):
                date_from = None
                date_to = fields.Date.from_string(options['date']['date'])
            else:
                date_from = fields.Date.from_string(
                    options['date']['date_from'])
                date_to = fields.Date.from_string(options['date']['date_to'])
        elif 'today' in options_filter:
            if not self.has_single_date_filter(options):
                date_from = request.env.user.company_id.compute_fiscalyear_dates(date_to)['date_from']
        elif 'month' in options_filter:
            date_from, date_to = date_utils.get_month(date_to)
        elif 'quarter' in options_filter:
            date_from, date_to = date_utils.get_quarter(date_to)
        elif 'year' in options_filter:
            company_fiscalyear_dates = request.env.user.company_id.compute_fiscalyear_dates(date_to)
            date_from = company_fiscalyear_dates['date_from']
            date_to = company_fiscalyear_dates['date_to']
        else:
            raise UserError('Programmation Error: Unrecognized parameter %s in date filter!' % str(options_filter))

        period_vals = self._get_dates_period(options, date_from, date_to)
        if 'last' in options_filter:
            period_vals = self._get_dates_previous_period(options, period_vals)

        options['date'].update(create_vals(period_vals))

    def _get_dates_period(self, options, date_from, date_to, period_type=None):
        def match(dt_from, dt_to):
            if self.has_single_date_filter(options):
                return (date_to or date_from) == dt_to
            else:
                return (dt_from, dt_to) == (date_from, date_to)

        string = None
        # If no date_from or not date_to, we are unable to determine a period
        if not period_type:
            date = date_to or date_from
            company_fiscalyear_dates = request.env.user.company_id.compute_fiscalyear_dates(date)
            if match(company_fiscalyear_dates['date_from'], company_fiscalyear_dates['date_to']):
                period_type = 'fiscalyear'
                if company_fiscalyear_dates.get('record'):
                    string = company_fiscalyear_dates['record'].name
            elif match(*date_utils.get_month(date)):
                period_type = 'month'
            elif match(*date_utils.get_quarter(date)):
                period_type = 'quarter'
            elif match(*date_utils.get_fiscal_year(date)):
                period_type = 'year'
            else:
                period_type = 'custom'

        if not string:
            fy_day = request.env.user.company_id.fiscalyear_last_day
            fy_month = request.env.user.company_id.fiscalyear_last_month
            if self.has_single_date_filter(options):
                string = _('As of %s') % (format_date(
                    request.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)))
            elif period_type == 'year' or (period_type == 'fiscalyear' and (date_from, date_to) == date_utils.get_fiscal_year(date_to)):
                string = date_to.strftime('%Y')
            elif period_type == 'fiscalyear' and (date_from, date_to) == date_utils.get_fiscal_year(date_to, day=fy_day, month=fy_month):
                string = '%s - %s' % (date_to.year - 1, date_to.year)
            elif period_type == 'month':
                string = format_date(request.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT), date_format='MMM YYYY')
            elif period_type == 'quarter':
                quarter_names = get_quarter_names('abbreviated', locale=request.env.context.get('lang') or 'en_US')
                string = u'%s\N{NO-BREAK SPACE}%s' % (quarter_names[date_utils.get_quarter_number(date_to)], date_to.year)
            else:
                dt_from_str = format_date(request.env, date_from.strftime(DEFAULT_SERVER_DATE_FORMAT))
                dt_to_str = format_date(request.env, date_to.strftime(DEFAULT_SERVER_DATE_FORMAT))
                string = _('From %s \n to  %s') % (dt_from_str, dt_to_str)

        return {
            'string': string,
            'period_type': period_type,
            'date_from': date_from,
            'date_to': date_to,
        }

    def _get_dates_previous_period(self, options, period_vals):
        period_type = period_vals['period_type']
        date_from = period_vals['date_from']
        date_to = period_vals['date_to']

        if not date_from or not date_to:
            date = (date_from or date_to).replace(
                day=1) - datetime.timedelta(days=1)
            return self._get_dates_period(
                options, None, date, period_type=period_type)

        date_to = date_from - datetime.timedelta(days=1)
        if period_type == 'fiscalyear':
            company_fiscalyear_dates = request.env.user.company_id.compute_fiscalyear_dates(date_to)
            return self._get_dates_period(
                options, company_fiscalyear_dates['date_from'],
                company_fiscalyear_dates['date_to'])
        if period_type == 'month':
            return self._get_dates_period(
                options, *date_utils.get_month(date_to), period_type='month')
        if period_type == 'quarter':
            return self._get_dates_period(
                options, *date_utils.get_quarter(date_to),
                period_type='quarter')
        if period_type == 'year':
            return self._get_dates_period(
                options, *date_utils.get_fiscal_year(
                    date_to), period_type='year')
        date_from = date_to - datetime.timedelta(
            days=(date_to - date_from).days)
        return self._get_dates_period(options, date_from, date_to)

    def _get_dates_previous_year(self, options, period_vals):
        period_type = period_vals['period_type']
        date_from = period_vals['date_from']
        date_to = period_vals['date_to']

        if not date_from or not date_to:
            date_to = date_from or date_to
            date_from = None

        date_to = date_to - relativedelta(years=1)
        # Take care about the 29th february.
        # Moving from 2017-02-28 -> 2016-02-28 is wrong! It must be 2016-02-29.
        if period_type == 'month':
            date_from, date_to = date_utils.get_month(date_to)
        elif date_from:
            date_from = date_from - relativedelta(years=1)
        return self._get_dates_period(
            options, date_from, date_to, period_type=period_type)

    def _plan_prepare_values(self, projects, options):
        currency = request.env.user.company_id.currency_id
        if options and options['option_value'] == 'ifrs_currency':
            currency = request.env.user.company_id.group_currency_id
        values = {
            'currency': currency,
            'projects': projects,
        }
        # -- Invoice Buttons
        values['inv_buttons'] = self._plan_get_inv_button(projects, options)
        values['unpaid_inv_buttons'] = self._plan_get_unpaid_inv_button(projects, options)
        values['supplier_inv_buttons'] = self._plan_get_supplier_inv_button(projects, options)
        values['inv_payment_buttons'] = self._plan_get_inv_payment_button(projects, options)
        values['supplier_inv_payment_buttons'] = self._plan_get_supplier_inv_payment_button(projects, options)

        # -- Sale Budget Buttons continue UNPAID, TOTAL DUE NOT YET COMPUTED
        values['budget_buttons_sales'] = self._plan_get_budget_button_sales(projects, options)
        values['budget_buttons_purchases'] = self._plan_get_budget_button_purchases(projects, options)
        values['budget_buttons_timesheets'] = self._plan_get_budget_button_timesheets(projects, options)
        values['budget_buttons_expense'] = self._plan_get_budget_button_expense(projects, options)

        # -- Sale Buttons
        values['sale_buttons'] = self._plan_get_sale_button(projects, options)

        # -- Purchase Buttons
        values['purchase_buttons'] = self._plan_get_purchase_button(projects, options)

        # -- Timesheet Buttons
        values['timesheet_buttons'] = self._plan_get_timesheet_button(projects, options)

        # -- Journal Buttons
        values['journal_items_buttons'] = self._plan_get_journal_item_button(projects, options)

        # -- Expense Buttons
        values['expense_buttons'] = self._plan_get_expense_button(projects, options)

        # -- child parent navigation
        values['child_parent_navigation'] = self._plan_get_child_parent(projects, options)

        # -- Dashboard Data
        values['dashboard_data'] = self._get_dashboard_data(projects, options)

        # -- Total Due Data
        values['total_due'] = self._get_total_due(projects, options)
        return values

    def _get_list_account(self, project_id):
        list_aac = []
        for proj in project_id:
            list_aac.append(proj.id)
        return list_aac

    def _get_data(self, project_id, invoice_type, state, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        AccountInvoiceLine = request.env['account.invoice.line']
        searchtemp = \
            [
                ('account_analytic_id', 'child_of', list_aac),
                ('invoice_id.state', 'in', state),
                ('invoice_id.type', 'in', invoice_type),
            ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('invoice_id.date_invoice', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('invoice_id.date_invoice', '<=', options['date']['date_to']),
            )
        invoice_line_ids = AccountInvoiceLine.search(searchtemp)
        invoice_ids = invoice_line_ids.mapped('invoice_id')

        inv_domain = [
            ('id', 'in', invoice_ids.ids), ('type', 'in', invoice_type)]
        list_buttons.append({
            'name': _('Invoices'),
            'count': request.env['account.invoice'].search_count(inv_domain),
            'res_model': 'account.invoice',
            'domain': inv_domain,
        })
        return list_buttons

    def _plan_get_inv_button(self, project_id, options):
        list_buttons = self._get_data(
            project_id, invoice_type=['out_invoice', 'out_refund'],
            state=['open', 'paid'], options=options)
        return list_buttons

    def _plan_get_inv_payment_button(self, project_id, options):
        list_buttons = self._get_data(
            project_id,
            invoice_type=['out_invoice', 'out_refund'],
            state=['paid'], options=options)
        return list_buttons

    def _plan_get_unpaid_inv_button(self, project_id, options):
        list_buttons = self._get_data(
            project_id,
            invoice_type=['out_invoice', 'out_refund'],
            state=['open'], options=options)
        return list_buttons

    def _plan_get_supplier_inv_button(self, project_id, options):
        list_buttons = self._get_data(
            project_id,
            invoice_type=['in_invoice', 'in_refund'],
            state=['open', 'paid'], options=options)
        return list_buttons

    def _plan_get_supplier_inv_payment_button(self, project_id, options):
        list_buttons = self._get_data(
            project_id,
            invoice_type=['in_invoice', 'in_refund'],
            state=['paid'], options=options)
        return list_buttons

    def _plan_get_sale_button(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        sale_domain = [
            ('analytic_account_id', 'child_of', list_aac),
            ('state', 'in', ['sale', 'done']),
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            sale_domain.append(
                ('confirmation_date', '>=', options['date']['date_from'])
            )
            sale_domain.append(
                ('confirmation_date', '<=', options['date']['date_to']),
            )

        list_buttons.append({
            'name': _('Sales'),
            'count': request.env['sale.order'].search_count(sale_domain),
            'res_model': 'sale.order',
            'domain': sale_domain,
        })
        return list_buttons

    def _plan_get_child_parent(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        parent_child_domain = [
            '|',
            ('id', 'child_of', list_aac),
            ('id', 'parent_of', list_aac),
        ]

        list_buttons.append({
            'name': _('Analytic Account'),
            'count': request.env['account.analytic.account'].search_count(parent_child_domain),
            'res_model': 'account.analytic.account',
            'domain': parent_child_domain,
        })
        return list_buttons

    def _plan_get_purchase_button(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        PurchaseOrderLine = request.env['purchase.order.line']
        searchtemp = [
            ('account_analytic_id', 'child_of', list_aac),
            ('order_id.state', 'in', ['purchase', 'done']),
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            searchtemp.append(
                ('date_planned', '>=', options['date']['date_from'])
            )
            searchtemp.append(
                ('date_planned', '<=', options['date']['date_to']),
            )

        purchase_order_line_ids = PurchaseOrderLine.search(searchtemp)
        purchase_ids = purchase_order_line_ids.mapped('order_id')
        purchase_domain = [('id', 'in', purchase_ids.ids)]

        list_buttons.append({
            'name': _('Purchase'),
            'count': request.env['purchase.order'].search_count(purchase_domain),
            'res_model': 'purchase.order',
            'domain': purchase_domain,
        })
        return list_buttons

    def _plan_get_timesheet_button(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        timesheet_domain = [
            ('account_id', 'child_of', list_aac),
            ('is_timesheet', '=', True),
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            timesheet_domain.append(
                ('date', '>=', options['date']['date_from'])
            )
            timesheet_domain.append(
                ('date', '<=', options['date']['date_to']),
            )

        list_buttons.append({
            'name': _('Timesheets'),
            'count': request.env['account.analytic.line'].search_count(timesheet_domain),
            'res_model': 'account.analytic.line',
            'domain': timesheet_domain,
        })
        return list_buttons

    def _plan_get_journal_item_button(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        journal_domain = [
            ('analytic_account_id', 'child_of', list_aac),
            ('journal_id.fal_is_timesheet_journal', '=', True),
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            journal_domain.append(
                ('date', '>=', options['date']['date_from'])
            )
            journal_domain.append(
                ('date', '<=', options['date']['date_to']),
            )

        list_buttons.append({
            'name': _('Journal Items'),
            'count': request.env['account.move.line'].search_count(journal_domain),
            'res_model': 'account.move.line',
            'domain': journal_domain,
        })
        return list_buttons

    def _plan_get_expense_button(self, project_id, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        expense_domain = [
            ('analytic_account_id', 'child_of', list_aac),
            ('state', 'in', ['post', 'done']),
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            expense_domain.append(
                ('date', '>=', options['date']['date_from'])
            )
            expense_domain.append(
                ('date', '<=', options['date']['date_to']),
            )

        list_buttons.append({
            'name': _('Sales'),
            'count': request.env['hr.expense'].search_count(expense_domain),
            'res_model': 'hr.expense',
            'domain': expense_domain,
        })
        return list_buttons

    def _plan_get_budget_button(self, project_id, oid, options):
        list_buttons = []
        list_aac = self._get_list_account(project_id)

        data_obj = request.env['ir.model.data']
        mdl = 'fal_project_budget'
        oid = oid
        res_id = '.'.join([mdl, oid])
        tag_id = data_obj.xmlid_to_res_id(res_id)
        domain = [
            ('fal_budget_tags_ids', 'in', [tag_id]),
            ('project_id', 'child_of', list_aac)
        ]
        if options and options['date']['date_from'] and options['date']['date_to']:
            domain.append(
                ('date_from', '>=', options['date']['date_from'])
            )
            domain.append(
                ('date_to', '<=', options['date']['date_to']),
            )

        list_buttons.append({
            'count': request.env['fal.project.budget.line'].search_count(
                domain),
            'res_model': 'fal.project.budget.line',
            'domain': domain,
        })
        return list_buttons

    def _plan_get_budget_button_sales(self, project_id, options):
        list_button = self._plan_get_budget_button(
            project_id, oid='fal_project_budget_tags_sales', options=options)
        return list_button

    def _plan_get_budget_button_purchases(self, project_id, options):
        list_button = self._plan_get_budget_button(
            project_id, oid='fal_project_budget_tags_purchases',
            options=options)
        return list_button

    def _plan_get_budget_button_timesheets(self, project_id, options):
        list_button = self._plan_get_budget_button(
            project_id, oid='fal_project_budget_tags_employee_timesheets',
            options=options)
        return list_button

    def _plan_get_budget_button_expense(self, project_id, options):
        list_button = self._plan_get_budget_button(
            project_id, oid='fal_project_budget_tags_mission_expenses',
            options=options)
        return list_button

    def _get_total_due(self, project_id, options):
        list_value = []
        notdue = 0.0
        v30d = 0.0
        v60d = 0.0
        v61d = 0.0
        for x in project_id:
            val_notdue = x.get_total_due('notdue', options)
            if not val_notdue:
                val_notdue = 0.0

            val_30d = x.get_total_due('30d', options)
            if not val_30d:
                val_30d = 0.0

            val_60d = x.get_total_due('60d', options)
            if not val_60d:
                val_60d = 0.0

            val_61d = x.get_total_due('61d', options)
            if not val_61d:
                val_61d = 0.0
            notdue += val_notdue
            v30d += val_30d
            v60d += val_60d
            v61d += val_61d
        list_value.append({
            'fal_customer_invoiced_total_not_due': notdue,
            'fal_customer_invoiced_total_due30d': v30d,
            'fal_customer_invoiced_total_due60d': v60d,
            'fal_customer_invoiced_total_due61d': v61d
        })
        return list_value

    def _get_dashboard_data(self, project_id, options):
        list_value = []
        fal_sale_order_total = 0.0
        fal_sale_order_count = 0
        fal_customer_invoiced_total = 0.0
        fal_customer_invoiced_count = 0
        fal_customer_payment_total = 0.0
        fal_customer_payment_count = 0
        fal_purchase_order_total = 0.0
        fal_purchase_order_count = 0
        fal_supplier_invoiced_total = 0.0
        fal_supplier_invoiced_count = 0
        fal_supplier_payment_total = 0.0
        fal_supplier_payment_count = 0
        fal_timesheet_cost_total = 0.0
        fal_timesheet_cost_count = 0
        fal_timesheet_cost_total_hour = 0
        fal_mission_expense_total = 0.0
        fal_mission_expense_count = 0
        fal_sale_budget_total = 0.0
        fal_purchase_budget_total = 0.0
        fal_mission_expense_budget_total = 0.0
        fal_timesheet_budget_total = 0.0
        fal_timesheet_budget_total_qty = 0
        fal_purchase_budget_total_termination = 0.0
        fal_timesheet_budget_total_termination = 0
        fal_timesheet_budget_total_qty_termination = 0
        fal_mission_expense_budget_total_termination = 0.0

        fal_customer_invoiced_percentage = 0
        fal_customer_payment_percentage = 0
        fal_purchase_order_percentage = 0
        fal_supplier_invoiced_percentage = 0
        fal_timesheet_cost_percentage = 0
        fal_mission_expense_percentage = 0
        fal_gross_margin_to_percentage = 0

        fal_gross_margin_order_percentage = 0

        fal_gross_margin_termination_percentage = 0
        fal_gross_margin_gap_percentage = 0
        fal_variable_cost_margin_to_percentage = 0
        fal_variable_cost_margin_order_percentage = 0
        fal_variable_cost_margin_termination_percentage = 0
        fal_variable_cost_margin_gap_percentage = 0
        fal_invoiced_gross_margin_to_percentage = 0
        fal_invoiced_variable_cost_margin_percentage = 0
        summary = ''
        for analytic_account in project_id:
            summary = analytic_account.summary
            # SEARCH
            # Sale Order
            sale_order_search = analytic_account._prepare_order_search('sale', options)
            fal_sale_order_total += sale_order_search['fal_total']
            fal_sale_order_count += sale_order_search['fal_count']
            # ------------------------
            # Invoice Sale Order
            invoice_line_search = analytic_account._prepare_order_search(
                'saleinv', options)
            fal_customer_invoiced_total += invoice_line_search['fal_total']
            fal_customer_invoiced_count += invoice_line_search['fal_count']
            # --------------------------------
            # Customer Payment
            customer_payment_search = analytic_account._prepare_move_search(
                'customer', options)
            fal_customer_payment_total += customer_payment_search['fal_total']
            fal_customer_payment_count += customer_payment_search['fal_count']
            # ------------------------------------
            # Purchase Order
            purchase_order_search = analytic_account._prepare_order_search(
                'purchase', options)
            fal_purchase_order_total += purchase_order_search['fal_total']
            fal_purchase_order_count += purchase_order_search['fal_count']
            # ---------------------------------
            # Invoice Purchase Order
            supplier_invoice_line_search = analytic_account._prepare_order_search('purcinv', options)
            fal_supplier_invoiced_total += supplier_invoice_line_search['fal_total']
            fal_supplier_invoiced_count += supplier_invoice_line_search['fal_count']
            # --------------------------------------------
            # Supplier Payment
            supplier_payment_search = analytic_account._prepare_move_search(
                'supplier', options)
            fal_supplier_payment_total += supplier_payment_search['fal_total']
            fal_supplier_payment_count += supplier_payment_search['fal_count']
            # -------------------------------------------
            # Timesheet Journal
            timesheet_journal_search = analytic_account._prepare_move_search(
                'timesheet', options)
            fal_timesheet_cost_total += timesheet_journal_search['fal_total']
            # ------------------------------------------
            # Timesheet Cost
            timesheet_cost_count_search = analytic_account._prepare_timesheet_cost_count_search(options)
            fal_timesheet_cost_count += timesheet_cost_count_search['fal_timesheet_cost_count']
            fal_timesheet_cost_total_hour += timesheet_cost_count_search['fal_timesheet_cost_total_hour']
            # -------------------------------------------
            # Mission Expense Total
            mission_expense_total_search = analytic_account._prepare_move_search('mission', options)
            fal_mission_expense_total += mission_expense_total_search['fal_total']
            # -------------------------------
            # Mission Expense Count
            mission_expense_count_search = analytic_account._prepare_mission_expense_count_search(options)
            fal_mission_expense_count += mission_expense_count_search['fal_mission_expense_count']
            # ------------------------------------------
            # Project Budget Sale
            project_budget_sale_search = analytic_account._prepare_budget_search('sale', options)
            fal_sale_budget_total += project_budget_sale_search['fal_total']
            # ------------------------------------------
            # Project Budget Purchase
            project_budget_purchase_search = analytic_account._prepare_budget_search('purchase', options)
            fal_purchase_budget_total += abs(project_budget_purchase_search['fal_total'])
            # --------------------------------
            # Project Budget Mission Expense
            project_budget_mission_expense_search = analytic_account._prepare_budget_search('mission', options)
            fal_mission_expense_budget_total += abs(project_budget_mission_expense_search['fal_total'])
            # ---------------------------------------
            # Project Employee Timesheet Expense
            project_budget_employee_timesheet_search = analytic_account._prepare_budget_search('employee', options)
            fal_timesheet_budget_total += abs(project_budget_employee_timesheet_search['fal_total'])
            fal_timesheet_budget_total_qty += project_budget_employee_timesheet_search['fal_qty']
            # ---------------------------------------------
            # Purchase Project Budget Termination
            project_purchase_budget_termination_search = analytic_account._prepare_termination_search('purchase', options)
            fal_purchase_budget_total_termination += abs(project_purchase_budget_termination_search['fal_total'])
            # ----------------------------------------------
            # Timesheet Project Budget Amount & Qty Termination
            project_timesheet_budget_termination_search = analytic_account._prepare_termination_search('employee', options)
            fal_timesheet_budget_total_termination += abs(project_timesheet_budget_termination_search['fal_total'])
            fal_timesheet_budget_total_qty_termination += project_timesheet_budget_termination_search['fal_qty']
            # ----------------------------------
            # Mission Expense Project Budget Termination
            project_mission_expense_budget_termination_search = analytic_account._prepare_termination_search('mission', options)
            fal_mission_expense_budget_total_termination += abs(project_mission_expense_budget_termination_search['fal_total'])

        # CALCULATION PROCESS
        # ------------------------------
        if fal_sale_order_total:
            so_total = fal_sale_order_total
            inv_total = fal_customer_invoiced_total
            x = (so_total - inv_total)
            fal_customer_invoiced_percentage = inv_total / so_total * 100
        # ----------------------
        if fal_sale_order_total:
            so_total = fal_sale_order_total
            pay_total = fal_customer_payment_total
            x = (so_total - pay_total)
            # fal_customer_payment_percentage = x / so_total * 100
            fal_customer_payment_percentage = pay_total / so_total * 100

        # -----------------------------
        termination = fal_purchase_budget_total_termination
        total = fal_purchase_order_total
        fal_purchase_order_total_remaining_order = termination - total
        # -----------------------------------
        if fal_purchase_budget_total_termination:
            total = fal_purchase_order_total_remaining_order
            termination = fal_purchase_budget_total_termination
            fal_purchase_order_percentage = total / termination * 100
        # -----------------------------------
        if fal_purchase_budget_total_termination:
            termination = fal_purchase_budget_total_termination
            invoiced = fal_supplier_invoiced_total
            fal_supplier_invoiced_percentage = \
                (termination - invoiced) / termination * 100
        # -------------------------------
        qty = fal_timesheet_budget_total_qty_termination
        hour = fal_timesheet_cost_total_hour
        fal_timesheet_cost_total_remaining_hour = qty - hour
        if fal_timesheet_budget_total_termination:
            termination = fal_timesheet_budget_total_termination
            cost = fal_timesheet_cost_total
            fal_timesheet_cost_percentage = \
                (termination - cost) / termination * 100
        # ----------------------------
        term = fal_mission_expense_budget_total_termination
        exp = fal_mission_expense_total
        fal_mission_expense_total_remaining_expense = term - exp
        if fal_mission_expense_budget_total_termination:
            term = fal_mission_expense_budget_total_termination
            exp = fal_mission_expense_total
            fal_mission_expense_percentage = (term - exp) / term * 100
        # -----------------------------------
        budget = fal_purchase_budget_total

        fal_gross_margin_to = fal_sale_budget_total - budget
        if fal_sale_budget_total:
            grs = fal_gross_margin_to
            so = fal_sale_budget_total
            fal_gross_margin_to_percentage = grs / so * 100
        # -----------------------------------

        fal_gross_margin_order = fal_sale_order_total - fal_purchase_order_total
        if fal_sale_order_total:
            grs = fal_gross_margin_order
            so = fal_sale_order_total
            fal_gross_margin_order_percentage = grs / so * 100

        cust = fal_customer_invoiced_total
        supp = fal_supplier_invoiced_total
        fal_gross_margin_termination = cust - supp
        if fal_customer_invoiced_total:
            grs = fal_gross_margin_termination
            inv = fal_customer_invoiced_total
            fal_gross_margin_termination_percentage = grs / inv * 100

        margin = fal_gross_margin_termination
        tshee = fal_timesheet_cost_total
        exp = fal_mission_expense_total
        fal_variable_cost_margin_termination = margin - tshee - exp
        if fal_sale_order_total:
            margin = fal_variable_cost_margin_termination
            so = fal_sale_order_total
            fal_variable_cost_margin_termination_percentage = \
                margin / so * 100
        # --------------------------------------------
        term = fal_gross_margin_termination
        fal_gross_margin_gap = fal_gross_margin_to - term
        if fal_gross_margin_to:
            gap = fal_gross_margin_gap
            to = fal_gross_margin_to
            fal_gross_margin_gap_percentage = gap / to * 100
        # -----------------------------------------
        margin = fal_gross_margin_to
        tshe = fal_timesheet_budget_total
        exp = fal_mission_expense_budget_total
        fal_variable_cost_margin_to = margin - tshe - exp
        if fal_sale_budget_total:
            margin = fal_variable_cost_margin_to
            so = fal_sale_budget_total
            fal_variable_cost_margin_to_percentage = margin / so * 100

        margin = fal_gross_margin_order
        tshe = fal_timesheet_cost_total
        exp = fal_mission_expense_total
        fal_variable_cost_margin_order = margin - tshe - exp
        if fal_sale_order_total:
            margin = fal_variable_cost_margin_order
            so = fal_sale_order_total
            fal_variable_cost_margin_order_percentage = margin / so * 100

        to = fal_variable_cost_margin_to
        term = fal_variable_cost_margin_termination
        fal_variable_cost_margin_gap = to - term
        if fal_variable_cost_margin_to:
            gap = fal_variable_cost_margin_gap
            to = fal_variable_cost_margin_to
            fal_variable_cost_margin_gap_percentage = gap / to * 100
        # ------------------------------------
        cust = fal_customer_invoiced_total
        supp = fal_supplier_invoiced_total
        fal_invoiced_gross_margin_to = cust - supp
        if fal_customer_invoiced_total:
            grs = fal_invoiced_gross_margin_to
            inv = fal_customer_invoiced_total
            fal_invoiced_gross_margin_to_percentage = grs / inv * 100
        # ------------------------------------
        grs = fal_invoiced_gross_margin_to
        cost = fal_timesheet_cost_total
        exp = fal_mission_expense_total
        fal_invoiced_variable_cost_margin = grs - cost - exp
        if fal_customer_invoiced_total:
            x = fal_invoiced_variable_cost_margin
            y = fal_customer_invoiced_total
            fal_invoiced_variable_cost_margin_percentage = x / y * 100

        list_value.append({
            'fal_sale_order_total': fal_sale_order_total,
            'fal_sale_order_count': fal_sale_order_count,
            'fal_customer_invoiced_total': fal_customer_invoiced_total,
            'fal_customer_invoiced_count': fal_customer_invoiced_count,
            'fal_customer_invoiced_percentage':
            floor(fal_customer_invoiced_percentage),
            'fal_customer_payment_total': fal_customer_payment_total,
            'fal_customer_payment_count': fal_customer_payment_count,
            'fal_customer_payment_percentage':
            floor(fal_customer_payment_percentage),
            'fal_purchase_order_total': fal_purchase_order_total,
            'fal_purchase_order_count': fal_purchase_order_count,
            'fal_purchase_order_total_remaining_order':
            fal_purchase_order_total_remaining_order,
            'fal_purchase_order_percentage': floor(fal_purchase_order_percentage),
            'fal_supplier_invoiced_total': fal_supplier_invoiced_total,
            'fal_supplier_invoiced_count': fal_supplier_invoiced_count,
            'fal_supplier_invoiced_percentage':
            floor(fal_supplier_invoiced_percentage),
            'fal_supplier_payment_total': fal_supplier_payment_total,
            'fal_supplier_payment_count': fal_supplier_payment_count,
            'fal_timesheet_cost_total': fal_timesheet_cost_total,
            'fal_timesheet_cost_count': fal_timesheet_cost_count,
            'fal_timesheet_cost_total_hour': int(fal_timesheet_cost_total_hour),
            'fal_timesheet_cost_total_remaining_hour':
            int(fal_timesheet_cost_total_remaining_hour),
            'fal_timesheet_cost_percentage': floor(fal_timesheet_cost_percentage),
            'fal_mission_expense_total': fal_mission_expense_total,
            'fal_mission_expense_total_remaining_expense':
            fal_mission_expense_total_remaining_expense,
            'fal_mission_expense_count': fal_mission_expense_count,
            'fal_mission_expense_percentage':
            floor(fal_mission_expense_percentage),
            'fal_gross_margin_order': fal_gross_margin_order,
            'fal_gross_margin_order_percentage':
            floor(fal_gross_margin_order_percentage),
            'fal_gross_margin_to': fal_gross_margin_to,
            'fal_gross_margin_to_percentage':
            floor(fal_gross_margin_to_percentage),
            'fal_gross_margin_termination': fal_gross_margin_termination,
            'fal_gross_margin_termination_percentage':
            floor(fal_gross_margin_termination_percentage),
            'fal_gross_margin_gap': fal_gross_margin_gap,
            'fal_gross_margin_gap_percentage':
            floor(fal_gross_margin_gap_percentage),
            'fal_variable_cost_margin_to': fal_variable_cost_margin_to,
            'fal_variable_cost_margin_order': fal_variable_cost_margin_order,
            'fal_variable_cost_margin_to_percentage':
            floor(fal_variable_cost_margin_to_percentage),
            'fal_variable_cost_margin_order_percentage':
            floor(fal_variable_cost_margin_order_percentage),
            'fal_variable_cost_margin_termination':
            fal_variable_cost_margin_termination,
            'fal_variable_cost_margin_termination_percentage':
            floor(fal_variable_cost_margin_termination_percentage),
            'fal_variable_cost_margin_gap': fal_variable_cost_margin_gap,
            'fal_variable_cost_margin_gap_percentage':
            floor(fal_variable_cost_margin_gap_percentage),
            'fal_invoiced_gross_margin_to': fal_invoiced_gross_margin_to,
            'fal_invoiced_gross_margin_to_percentage':
            floor(fal_invoiced_gross_margin_to_percentage),
            'fal_invoiced_variable_cost_margin':
            fal_invoiced_variable_cost_margin,
            'fal_invoiced_variable_cost_margin_percentage':
            floor(fal_invoiced_variable_cost_margin_percentage),
            'fal_sale_budget_total': fal_sale_budget_total,
            'fal_purchase_budget_total': fal_purchase_budget_total,
            'fal_mission_expense_budget_total':
            fal_mission_expense_budget_total,
            'fal_timesheet_budget_total': fal_timesheet_budget_total,
            'fal_timesheet_budget_total_qty':
            int(fal_timesheet_budget_total_qty),
            'fal_purchase_budget_total_termination':
            fal_purchase_budget_total_termination,
            'fal_timesheet_budget_total_termination':
            fal_timesheet_budget_total_termination,
            'fal_timesheet_budget_total_qty_termination':
            int(fal_timesheet_budget_total_qty_termination),
            'fal_mission_expense_budget_total_termination':
            fal_mission_expense_budget_total_termination,
            'summary': summary,
        })
        return list_value

    @http.route('/fal/dashboard/action', type='json', auth="user")
    def plan_stat_button(self, domain, res_model='account.analytic.line'):
        action = {
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'res_model': res_model,
            'view_type': 'tree',
            'domain': domain,
        }
        if res_model == 'account.analytic.line':
            ts_view_tree_id = request.env.ref(
                'hr_timesheet.hr_timesheet_line_tree').id
            ts_view_form_id = request.env.ref(
                'hr_timesheet.hr_timesheet_line_form').id
            action.update({
                'name': _('Timesheets'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'account.move.line':
            ts_view_tree_id = request.env.ref(
                'account.view_move_line_tree').id
            ts_view_form_id = request.env.ref(
                'account.view_move_line_form').id
            action.update({
                'name': _('Journal Items'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'account.analytic.account':
            ts_view_tree_id = request.env.ref(
                'fal_project_dashboard.view_project_account_analytic_account_kanban').id
            ts_view_form_id = request.env.ref(
                'analytic.view_account_analytic_account_form').id
            action.update({
                'name': _('Analytic Account'),
                'views': [
                    [ts_view_tree_id, 'kanban'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'account.invoice':
            get_type = eval(domain)
            if get_type[1] and get_type[1][2] and get_type[1][2] == ['in_invoice', 'in_refund']:
                ts_view_tree_id = request.env.ref('account.invoice_supplier_tree').id
                ts_view_form_id = request.env.ref('account.invoice_supplier_form').id
                name = 'Supplier Invoices'
            else:
                ts_view_tree_id = request.env.ref('account.invoice_tree').id
                ts_view_form_id = request.env.ref('account.invoice_form').id
                name = 'Customer Invoices'
            action.update({
                'name': _(name),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'fal.project.budget.line':
            ts_view_tree_id = request.env.ref(
                'fal_project_budget.view_fal_project_budget_line_tree').id
            ts_view_form_id = request.env.ref(
                'fal_project_budget.view_fal_project_budget_line_form').id
            action.update({
                'name': _('Budget'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'sale.order':
            ts_view_tree_id = request.env.ref('sale.view_order_tree').id
            ts_view_form_id = request.env.ref('sale.view_order_form').id
            action.update({
                'name': _('Sale Order'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'purchase.order':
            ts_view_tree_id = request.env.ref(
                'purchase.purchase_order_tree').id
            ts_view_form_id = request.env.ref(
                'purchase.purchase_order_form').id
            action.update({
                'name': _('Purchase Order'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        elif res_model == 'hr.expense':
            ts_view_tree_id = request.env.ref(
                'hr_expense.view_expenses_tree').id
            ts_view_form_id = request.env.ref(
                'hr_expense.hr_expense_view_form').id
            action.update({
                'name': _('Expenses'),
                'views': [
                    [ts_view_tree_id, 'list'],
                    [ts_view_form_id, 'form']],
            })
        return action
