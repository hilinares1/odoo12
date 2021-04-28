# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_user = None

    @api.model
    def _get_options(self, previous_options=None):
        if self.filter_user:
            self.filter_user_ids = []
        return super(AccountReport, self)._get_options(previous_options)

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('user_ids'):
            ctx['user_ids'] = self.env['res.users'].browse([int(user) for user in options['user_ids']])
        return ctx

    def get_report_informations(self, options):
        res = super(AccountReport, self).get_report_informations(options)
        options = self._get_options(options)
        searchview_dict = {'options': options, 'context': self.env.context}
        template_no_values = self.env['ir.ui.view'].render_template('fal_financial_report.search_template_salesperson', values=searchview_dict)
        if options.get('user'):
            searchview_dict['res_users'] = [(user.id, user.name) for user in self.env['res.users'].search([])] or False
            res['options']['selected_user_ids'] = [self.env['res.users'].browse(int(user)).name for user in options['user_ids']]
            template_with_values = self.env['ir.ui.view'].render_template('fal_financial_report.search_template_salesperson', values=searchview_dict)
            res['searchview_html'] = res['searchview_html'].replace(template_no_values, template_with_values)
        return res


class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    def _fal_get_partner_move_lines(self, account_type, date_from, target_move, period_length):
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        ctx = self._context
        periods = {}
        date_from = fields.Date.from_string(date_from)
        start = date_from - relativedelta(days=1)
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            periods[str(i)] = {
                'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                'stop': start.strftime('%Y-%m-%d'),
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop - relativedelta(days=1)

        res = []
        total = []
        partner_clause = ''
        cr = self.env.cr
        company_ids = self.env.context.get('company_ids', (self.env.user.company_id.id,))
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        #build the reconciliation clause to see what partner needs to be printed
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s', (date_from,))
        reconciled_after_date = []
        for row in cr.fetchall():
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        if ctx.get('partner_ids'):
            partner_clause = 'AND (l.partner_id IN %s)'
            arg_list += (tuple(ctx['partner_ids'].ids),)
        if ctx.get('partner_categories'):
            partner_clause += 'AND (l.partner_id IN %s)'
            partner_ids = self.env['res.partner'].search([('category_id', 'in', ctx['partner_categories'].ids)]).ids
            arg_list += (tuple(partner_ids or [0]),)
        if ctx.get('user_ids'):
            user_clause = 'AND (account_invoice.user_id IN %s)'
            arg_list += (tuple(ctx['user_ids'].ids),)
        arg_list += (date_from, tuple(company_ids))
        query = ''''''

        if ctx.get('user_ids'):
            query = '''
                SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
                FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id left join account_invoice on l.invoice_id = account_invoice.id, account_account, account_move am
                WHERE (l.account_id = account_account.id)
                    AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND ''' + reconciliation_clause + partner_clause + user_clause +'''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                ORDER BY UPPER(res_partner.name)'''
        else:
            query = '''
                SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
                FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
                WHERE (l.account_id = account_account.id)
                    AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND ''' + reconciliation_clause + partner_clause + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                ORDER BY UPPER(res_partner.name)'''

        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = ''
            if ctx.get('expected_date'):
                dates_query = '(COALESCE(l.expected_pay_date,l.date)'
            else:
                dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.date_maturity, l.date)'''
            if ctx.get('expected_date'):
                query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.expected_pay_date, l.date)'''
            else:
                query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.date_maturity, l.date)'''

            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount -= partial_line.amount

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        # This dictionary will store the not due amount of all partners
        undue_amounts = {}
        query = ''''''
        if ctx.get('expected_date'):
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.expected_pay_date,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s
                ORDER BY COALESCE(l.expected_pay_date, l.date)'''
        else:
            query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.internal_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s
                ORDER BY COALESCE(l.date_maturity, l.date)'''
        cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if partial_line.max_date <= date_from:
                    line_amount += partial_line.amount
            for partial_line in line.matched_credit_ids:
                if partial_line.max_date <= date_from:
                    line_amount -= partial_line.amount
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)

        return res, total, lines


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_user = True

    @api.model
    def _get_lines(self, options, line_id=None):
        if self.env.context.get('expected_date') or options.get('user') and options.get('user_ids') != []:
            sign = -1.0 if self.env.context.get('aged_balance') else 1.0
            lines = []
            account_types = [self.env.context.get('account_type')]
            results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(
                include_nullified_amount=True
            )._fal_get_partner_move_lines(
                account_types, self._context['date_to'], 'posted', 30)

            for values in results:
                if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                    continue
                vals = {
                    'id': 'partner_%s' % (values['partner_id'],),
                    'name': values['name'],
                    'level': 2,
                    'columns': [{'name': ''}] * 3 + [{'name': self.format_value(sign * v)} for v in [values['direction'], values['4'],
                                                                                                     values['3'], values['2'],
                                                                                                     values['1'], values['0'], values['total']]],
                    'trust': values['trust'],
                    'unfoldable': True,
                    'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
                }
                lines.append(vals)
                if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                    for line in amls[values['partner_id']]:
                        aml = line['line']
                        caret_type = 'account.move'
                        if aml.invoice_id:
                            caret_type = 'account.invoice.in' if aml.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                        elif aml.payment_id:
                            caret_type = 'account.payment'
                        date_view = aml.date_maturity
                        if self.env.context.get('expected_date'):
                            date_view = aml.expected_pay_date
                        vals = {
                            'id': aml.id,
                            'name': date_view or aml.date,
                            'caret_options': caret_type,
                            'level': 4,
                            'parent_id': 'partner_%s' % (values['partner_id'],),
                            'columns': [{'name': v} for v in [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]] +\
                                       [{'name': v} for v in [line['period'] == 6-i and self.format_value(sign * line['amount']) or '' for i in range(7)]],
                        }
                        lines.append(vals)
            if total and not line_id:
                total_line = {
                    'id': 0,
                    'name': _('Total'),
                    'class': 'total',
                    'level': 'None',
                    'columns': [{'name': ''}] * 3 + [{'name': self.format_value(sign * v)} for v in [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]],
                }
                lines.append(total_line)
            return lines
        else:
            return super(report_account_aged_partner, self)._get_lines(options, line_id)


class fal_report_account_aged_receivable(models.AbstractModel):
    _name = "fal.account.aged.receivable"
    _description = "Aged Receivable Expected Date"
    _inherit = "account.aged.partner"

    def _set_context(self, options):
        ctx = super(fal_report_account_aged_receivable, self)._set_context(options)
        ctx['account_type'] = 'receivable'
        ctx['expected_date'] = True
        return ctx

    def _get_report_name(self):
        return _("Aged Receivable Expected Date")

    def _get_templates(self):
        templates = super(fal_report_account_aged_receivable, self)._get_templates()
        templates['line_template'] = 'account_reports.line_template_aged_receivable_report'
        return templates


class fal_report_account_aged_payable(models.AbstractModel):
    _name = "fal.account.aged.payable"
    _description = "Aged Payable Expected Date"
    _inherit = "account.aged.partner"

    def _set_context(self, options):
        ctx = super(fal_report_account_aged_payable, self)._set_context(options)
        ctx['account_type'] = 'payable'
        ctx['aged_balance'] = True
        ctx['expected_date'] = True
        return ctx

    def _get_report_name(self):
        return _("Aged Payable Expected Date")

    def _get_templates(self):
        templates = super(fal_report_account_aged_payable, self)._get_templates()
        templates['line_template'] = 'account_reports.line_template_aged_payable_report'
        return templates
