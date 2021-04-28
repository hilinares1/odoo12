# -*- encoding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class TaxSelectionWizard(models.TransientModel):
    _name = "tax.selection.wizard"
    _description = 'Tax Selection Wizard'

    @api.onchange('date_start')
    def _onchange_date(self):
        res = {}
        if self.date_start:
            date = self.date_start
            last_day = date + relativedelta(day=1, months=+1, days=-1)
            self.date_end = last_day
            monthsplus3 = date + relativedelta(day=1, months=+4, days=-1)
            monthsmin3 = date + relativedelta(day=1, months=-3)
            res['domain'] = {'account_move_line': [
                ('date', '>=', monthsmin3),
                ('date', '<=', monthsplus3),
                ('tax_line_id', '!=', False),
                ('invoice_id.state', 'not in', ['draft', 'cancel']),
                ('reconciled', '=', False)
            ]}
            return res

    account_move_line = fields.Many2many(
        'account.move.line')
    date_start = fields.Date(
        string='Start Date')
    date_end = fields.Date(
        string='Ending Date')

    @api.multi
    def action_select(self):
        context = dict(self._context)
        note_obj = self.env['fal.tax.note']
        note_line_obj = self.env['fal.tax.note.line']
        amount = 0.0
        for item in self:
            for move in item.account_move_line:
                if move.debit != 0:
                    amount = -move.debit
                if move.credit != 0:
                    amount = move.credit
                note_line_obj.create({
                    'partner_id': move.partner_id.id,
                    'tax_note_id': note_obj.browse(
                        context.get('active_id')).id,
                    'name': move.name,
                    'invoice_id': move.invoice_id.id,
                    'move_line_id': move.id,
                    'number': move.invoice_id.number,
                    'account_id': move.account_id.id,
                    'analytic_account_id': move.analytic_account_id.id,
                    'tax_line_id': move.tax_line_id.id,
                    'amount': amount,
                    'untaxed_amount': move.invoice_id.amount_untaxed,
                    'amount_total': move.invoice_id.amount_total,
                })
