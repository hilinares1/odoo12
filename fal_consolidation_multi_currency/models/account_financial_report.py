# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import copy
import ast

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.pycompat import izip


class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    ifrs_basis = fields.Boolean('Allow IFRS basis mode', help='display the option to switch to IFRS basis mode')

    @api.model
    def _get_options(self, previous_options=None):
        self.filter_ifrs = False if self.ifrs_basis else None

        rslt = super(ReportAccountFinancialReport, self)._get_options(previous_options)

        return rslt

    @api.multi
    def _get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        if options.get('ir_filters'):
            line_obj = line_obj.with_context(periods=options.get('ir_filters'))

        currency_table = self._get_currency_table()
        domain, group_by = self._get_filter_info(options)

        if group_by:
            options['groups'] = {}
            options['groups']['fields'] = group_by
            options['groups']['ids'] = self._get_groups(domain, group_by)

        amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
        amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
        linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]

        # Change Start Here
        # Need the ifrs_basis to be passed here
        res = line_obj.with_context(
            cash_basis=options.get('cash_basis'),
            ifrs=options.get('ifrs'),
            filter_domain=domain,
        )._get_lines(self, currency_table, options, linesDicts)
        # Change End Here
        return res


class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    def _query_get_select_sum(self, currency_table):
        """ Little function to help building the SELECT statement when computing the report lines.

            @param currency_table: dictionary containing the foreign currencies (key) and their factor (value)
                compared to the current user's company currency
            @returns: the string and parameters to use for the SELECT
        """
        extra_params = []
        select = '''
            COALESCE(SUM(\"account_move_line\".balance), 0) AS balance,
            COALESCE(SUM(\"account_move_line\".amount_residual), 0) AS amount_residual,
            COALESCE(SUM(\"account_move_line\".debit), 0) AS debit,
            COALESCE(SUM(\"account_move_line\".credit), 0) AS credit
        '''
        # Change Start Here
        # IFRS Doesn't need Currency 
        if currency_table and not self.env.context.get('ifrs'):
        # Change End Here
            select = 'COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".balance * %s '
            select += 'ELSE \"account_move_line\".balance END), 0) AS balance, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".amount_residual * %s '
            select += 'ELSE \"account_move_line\".amount_residual END), 0) AS amount_residual, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".debit * %s '
            select += 'ELSE \"account_move_line\".debit END), 0) AS debit, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".credit * %s '
            select += 'ELSE \"account_move_line\".credit END), 0) AS credit'

        if self.env.context.get('cash_basis'):
            for field in ['debit', 'credit', 'balance']:
                #replace the columns selected but not the final column name (... AS <field>)
                number_of_occurence = len(select.split(field)) - 1
                select = select.replace(field, field + '_cash_basis', number_of_occurence - 1)
        # Change Start Here
        # Handle IFRS Change Debit/Credit
        elif self.env.context.get('ifrs'):
            for field in ['debit', 'credit', 'balance', 'amount_residual']:
                #replace the columns selected but not the final column name (... AS <field>)
                number_of_occurence = len(select.split(field)) - 1
                select = select.replace(field, 'fal_' + field + '_group_curr', number_of_occurence - 1)
        # Change End Here
        return select, extra_params

    def _get_with_statement(self, financial_report):
        """ This function allow to define a WITH statement as prologue to the usual queries returned by query_get().
            It is useful if you need to shadow a table entirely and let the query_get work normally although you're
            fetching rows from your temporary table (built in the WITH statement) instead of the regular tables.

            @returns: the WITH statement to prepend to the sql query and the parameters used in that WITH statement
            @rtype: tuple(char, list)
        """
        sql = ''
        params = []

        #Cashflow Statement
        #------------------
        #The cash flow statement has a dedicated query because because we want to make a complex selection of account.move.line,
        #but keep simple to configure the financial report lines.
        if financial_report == self.env.ref('account_reports.account_financial_report_cashsummary0'):
            # Get all available fields from account_move_line, to build the 'select' part of the query
            # Change Start Here
            # Need to manage IFRS
            if self.env.context.get('ifrs'):
                replace_columns = {
                    'date': 'ref.date',
                    'debit': 'CASE WHEN \"account_move_line\".debit > 0 THEN ref.matched_percentage * \"account_move_line\".fal_debit_group_curr ELSE 0 END AS debit',
                    'credit': 'CASE WHEN \"account_move_line\".credit > 0 THEN ref.matched_percentage * \"account_move_line\".fal_credit_group_curr ELSE 0 END AS credit',
                    'balance': 'ref.matched_percentage * \"account_move_line\".fal_balance_group_curr AS balance',
                    'amount_residual': 'ref.matched_percentage * \"account_move_line\".fal_amount_residual_group_curr AS amount_residual'
                }
            else:
                replace_columns = {
                    'date': 'ref.date',
                    'debit': 'CASE WHEN \"account_move_line\".debit > 0 THEN ref.matched_percentage * \"account_move_line\".debit ELSE 0 END AS debit',
                    'credit': 'CASE WHEN \"account_move_line\".credit > 0 THEN ref.matched_percentage * \"account_move_line\".credit ELSE 0 END AS credit',
                    'balance': 'ref.matched_percentage * \"account_move_line\".balance AS balance'
                }
            # Change End Here
            columns = []
            columns_2 = []
            for name, field in self.env['account.move.line']._fields.items():
                if not(field.store and field.type not in ('one2many', 'many2many')):
                    continue
                columns.append('\"account_move_line\".\"%s\"' % name)
                if name in replace_columns:
                    columns_2.append(replace_columns.get(name))
                else:
                    columns_2.append('\"account_move_line\".\"%s\"' % name)
            select_clause_1 = ', '.join(columns)
            select_clause_2 = ', '.join(columns_2)

            # Get moves having a line using a bank account in one of the selected journals.
            if self.env.context.get('journal_ids'):
                bank_journals = self.env['account.journal'].browse(self.env.context.get('journal_ids'))
            else:
                bank_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
            bank_accounts = bank_journals.mapped('default_debit_account_id') + bank_journals.mapped('default_credit_account_id')

            self._cr.execute('SELECT DISTINCT(move_id) FROM account_move_line WHERE account_id IN %s', [tuple(bank_accounts.ids)])
            bank_move_ids = tuple([r[0] for r in self.env.cr.fetchall()])

            # Avoid crash if there's no bank moves to consider
            if not bank_move_ids:
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE False)''', []

            # Fake domain to always get the join to the account_move_line__move_id table.
            fake_domain = [('move_id.id', '!=', None)]
            sub_tables, sub_where_clause, sub_where_params = self.env['account.move.line']._query_get(domain=fake_domain)
            tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=fake_domain + ast.literal_eval(self.domain))

            # Get moves having a line using a bank account.
            bank_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
            bank_accounts = bank_journals.mapped('default_debit_account_id') + bank_journals.mapped('default_credit_account_id')
            q = '''SELECT DISTINCT(\"account_move_line\".move_id)
                    FROM ''' + tables + '''
                    WHERE account_id IN %s
                    AND ''' + sub_where_clause
            p = [tuple(bank_accounts.ids)] + sub_where_params
            self._cr.execute(q, p)
            bank_move_ids = tuple([r[0] for r in self.env.cr.fetchall()])

            # Only consider accounts related to a bank/cash journal, not all liquidity accounts
            if self.code in ('CASHEND', 'CASHSTART'):
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE account_id in %s)''', [tuple(bank_accounts.ids)]

            # Avoid crash if there's no bank moves to consider
            if not bank_move_ids:
                return '''
                WITH account_move_line AS (
                    SELECT ''' + select_clause_1 + '''
                    FROM account_move_line
                    WHERE False)''', []

            # The following query is aliasing the account.move.line table to consider only the journal entries where, at least,
            # one line is touching a liquidity account. Counterparts are either shown directly if they're not reconciled (or
            # not reconciliable), either replaced by the accounts of the entries they're reconciled with.
            # Change Start Here
            # Need to manage IFRS
            if self.env.context.get('ifrs'):
                sql = '''
                    WITH account_move_line AS (

                        -- Part for the reconciled journal items
                        -- payment_table will give the reconciliation rate per account per move to consider
                        -- (so that an invoice with multiple payment terms would correctly display the income
                        -- accounts at the prorata of what hass really been paid)
                        WITH payment_table AS (
                            SELECT
                                aml2.move_id AS matching_move_id,
                                aml2.account_id,
                                aml.date AS date,
                                SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                    THEN 0
                                    ELSE part.fal_amount_group_curr / sub.total_per_account
                                END) AS matched_percentage
                            FROM account_partial_reconcile part
                            LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                            LEFT JOIN account_move_line aml2 ON aml2.id = part.credit_move_id
                            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                            LEFT JOIN account_account acc ON aml.account_id = acc.id
                            WHERE part.credit_move_id = aml2.id
                            AND acc.reconcile
                            AND aml.move_id IN %s
                            GROUP BY aml2.move_id, aml2.account_id, aml.date

                            UNION ALL

                            SELECT
                                aml2.move_id AS matching_move_id,
                                aml2.account_id,
                                aml.date AS date,
                                SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                    THEN 0
                                    ELSE part.fal_amount_group_curr / sub.total_per_account
                                END) AS matched_percentage
                            FROM account_partial_reconcile part
                            LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                            LEFT JOIN account_move_line aml2 ON aml2.id = part.debit_move_id
                            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                            LEFT JOIN account_account acc ON aml.account_id = acc.id
                            WHERE part.debit_move_id = aml2.id
                            AND acc.reconcile
                            AND aml.move_id IN %s
                            GROUP BY aml2.move_id, aml2.account_id, aml.date
                        )

                        SELECT ''' + select_clause_2 + '''
                        FROM account_move_line "account_move_line"
                        RIGHT JOIN payment_table ref ON ("account_move_line".move_id = ref.matching_move_id)
                        WHERE "account_move_line".account_id NOT IN (SELECT account_id FROM payment_table)
                        AND "account_move_line".move_id NOT IN %s

                        UNION ALL

                        -- Part for the unreconciled journal items.
                        -- Using amount_residual if the account is reconciliable is needed in case of partial reconciliation

                        SELECT ''' + select_clause_1.replace('"account_move_line"."fal_balance_group_curr"', 'CASE WHEN acc.reconcile THEN  "account_move_line".fal_amount_residual_group_curr ELSE "account_move_line".fal_balance_group_curr END AS balance_cash_basis') + '''
                        FROM account_move_line "account_move_line"
                        LEFT JOIN account_account acc ON "account_move_line".account_id = acc.id
                        WHERE "account_move_line".move_id IN %s
                        AND "account_move_line".account_id NOT IN %s
                    )
                '''
            else:
                sql = '''
                    WITH account_move_line AS (

                        -- Part for the reconciled journal items
                        -- payment_table will give the reconciliation rate per account per move to consider
                        -- (so that an invoice with multiple payment terms would correctly display the income
                        -- accounts at the prorata of what hass really been paid)
                        WITH payment_table AS (
                            SELECT
                                aml2.move_id AS matching_move_id,
                                aml2.account_id,
                                aml.date AS date,
                                SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                    THEN 0
                                    ELSE part.amount / sub.total_per_account
                                END) AS matched_percentage
                            FROM account_partial_reconcile part
                            LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                            LEFT JOIN account_move_line aml2 ON aml2.id = part.credit_move_id
                            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                            LEFT JOIN account_account acc ON aml.account_id = acc.id
                            WHERE part.credit_move_id = aml2.id
                            AND acc.reconcile
                            AND aml.move_id IN %s
                            GROUP BY aml2.move_id, aml2.account_id, aml.date

                            UNION ALL

                            SELECT
                                aml2.move_id AS matching_move_id,
                                aml2.account_id,
                                aml.date AS date,
                                SUM(CASE WHEN (aml.balance = 0 OR sub.total_per_account = 0)
                                    THEN 0
                                    ELSE part.amount / sub.total_per_account
                                END) AS matched_percentage
                            FROM account_partial_reconcile part
                            LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                            LEFT JOIN account_move_line aml2 ON aml2.id = part.debit_move_id
                            LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account FROM account_move_line GROUP BY move_id, account_id) sub ON (aml2.account_id = sub.account_id AND sub.move_id=aml2.move_id)
                            LEFT JOIN account_account acc ON aml.account_id = acc.id
                            WHERE part.debit_move_id = aml2.id
                            AND acc.reconcile
                            AND aml.move_id IN %s
                            GROUP BY aml2.move_id, aml2.account_id, aml.date
                        )

                        SELECT ''' + select_clause_2 + '''
                        FROM account_move_line "account_move_line"
                        RIGHT JOIN payment_table ref ON ("account_move_line".move_id = ref.matching_move_id)
                        WHERE "account_move_line".account_id NOT IN (SELECT account_id FROM payment_table)
                        AND "account_move_line".move_id NOT IN %s

                        UNION ALL

                        -- Part for the unreconciled journal items.
                        -- Using amount_residual if the account is reconciliable is needed in case of partial reconciliation

                        SELECT ''' + select_clause_1.replace('"account_move_line"."balance_cash_basis"', 'CASE WHEN acc.reconcile THEN  "account_move_line".amount_residual ELSE "account_move_line".balance END AS balance_cash_basis') + '''
                        FROM account_move_line "account_move_line"
                        LEFT JOIN account_account acc ON "account_move_line".account_id = acc.id
                        WHERE "account_move_line".move_id IN %s
                        AND "account_move_line".account_id NOT IN %s
                    )
                '''
            params = [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_move_ids)] + [tuple(bank_accounts.ids)]
        elif self.env.context.get('cash_basis'):
            #Cash basis option
            #-----------------
            #In cash basis, we need to show amount on income/expense accounts, but only when they're paid AND under the payment date in the reporting, so
            #we have to make a complex query to join aml from the invoice (for the account), aml from the payments (for the date) and partial reconciliation
            #(for the reconciled amount).
            user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
            if not user_types:
                return sql, params

            # Get all columns from account_move_line using the psql metadata table in order to make sure all columns from the account.move.line model
            # are present in the shadowed table.
            sql = "SELECT column_name FROM information_schema.columns WHERE table_name='account_move_line'"
            self.env.cr.execute(sql)
            columns = []
            columns_2 = []
            replace_columns = {'date': 'ref.date',
                                'debit_cash_basis': 'CASE WHEN aml.debit > 0 THEN ref.matched_percentage * aml.debit ELSE 0 END AS debit_cash_basis',
                                'credit_cash_basis': 'CASE WHEN aml.credit > 0 THEN ref.matched_percentage * aml.credit ELSE 0 END AS credit_cash_basis',
                                'balance_cash_basis': 'ref.matched_percentage * aml.balance AS balance_cash_basis'}
            for field in self.env.cr.fetchall():
                field = field[0]
                columns.append("\"account_move_line\".\"%s\"" % (field,))
                if field in replace_columns:
                    columns_2.append(replace_columns.get(field))
                else:
                    columns_2.append('aml.\"%s\"' % (field,))
            select_clause_1 = ', '.join(columns)
            select_clause_2 = ', '.join(columns_2)

            #we use query_get() to filter out unrelevant journal items to have a shadowed table as small as possible
            tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=self._get_aml_domain())
            sql = """WITH account_move_line AS (
              SELECT """ + select_clause_1 + """
               FROM """ + tables + """
               WHERE (\"account_move_line\".journal_id IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                 OR \"account_move_line\".move_id NOT IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s))
                 AND """ + where_clause + """
              UNION ALL
              (
               WITH payment_table AS (
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id, """ + tables + """
                   WHERE part.credit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
                 UNION ALL
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id, """ + tables + """
                   WHERE part.debit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
               )
               SELECT """ + select_clause_2 + """
                FROM account_move_line aml
                RIGHT JOIN payment_table ref ON aml.move_id = ref.move_id
                WHERE journal_id NOT IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                  AND aml.move_id IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s)
              )
            ) """
            params = [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)]
        return sql, params

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        value['no_format_name'] = value['name']
        if self.figure_type == 'float':
            # Change Start Here
            # If IFRS need to use group currency symbol
            if self.env.context.get('ifrs') and self.env.user.company_id.group_currency_id:
                currency_id = self.env.user.company_id.group_currency_id
            else:
                currency_id = self.env.user.company_id.currency_id
            # Change End Here
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
                value['class'] = 'number text-muted'
            value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            return value
        if self.figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            return value
        value['name'] = round(value['name'], 1)
        return value
