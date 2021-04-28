# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportJournal(models.AbstractModel):
    _inherit = 'report.account.report_journal'

    def _sum_debit_ifrs(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(fal_debit_group_curr) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    def _sum_credit_ifrs(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(fal_credit_group_curr) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    @api.model
    def _get_report_values(self, docids, data=None):
        result = super(ReportJournal, self)._get_report_values(docids, data)
        result['sum_credit_ifrs'] = self._sum_credit_ifrs
        result['sum_debit_ifrs'] = self._sum_debit_ifrs
        return result

    def _get_taxes(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = """
            SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
            FROM account_move_line_account_tax_rel rel, """ + query_get_clause[0] + """ 
            LEFT JOIN account_move am ON "account_move_line".move_id = am.id
            WHERE "account_move_line".id = rel.account_move_line_id
                AND am.state IN %s
                AND "account_move_line".journal_id IN %s
                AND """ + query_get_clause[1] + """
           GROUP BY rel.account_tax_id"""
        self.env.cr.execute(query, tuple(params))
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]


        res = {}
        for tax in self.env['account.tax'].browse(ids):
            # Change Start Here
            # Handle IFRS need
            self.env.cr.execute('SELECT sum(debit - credit), sum(fal_debit_group_curr - fal_credit_group_curr) FROM ' + query_get_clause[0] + ', account_move am '
                'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' AND tax_line_id = %s',
                tuple(params + [tax.id]))
            fetch_res = self.env.cr.fetchone() or 0
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': fetch_res[0] or 0.0,
                'tax_amount_ifrs': fetch_res[1] or 0.0,
            }
            if journal_id.type == 'sale':
                #sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res
