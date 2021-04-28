# coding: utf-8

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    doku_difference_amount = fields.Float('Doku Difference Amount', compute='_compute_difference_amount', store=True)

    @api.multi
    @api.depends('amount_total')
    def _compute_difference_amount(self):
        for record in self:
            check_margin_amount = round(record.amount_total) - record.amount_total
            record.doku_difference_amount = check_margin_amount


class account_payment(models.Model):
    _inherit = 'account.payment'

    def _create_payment_entry(self, amount):
        _logger.info("------------------------ _create_payment_entry")
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        if self.invoice_ids:
            aml_record = aml_obj.search([
                ('account_id.user_type_id.type', '=', 'liquidity'),
                ('move_id', '=', move.id),
            ])
            doku_payment_acquirer = self.env['payment.acquirer'].search(
                [('provider', '=', 'doku')])
            if self.invoice_ids[0].doku_difference_amount > 0:
                if aml_record and doku_payment_acquirer:
                    aml_record.write({
                        'debit': aml_record.debit + self.invoice_ids[0].doku_difference_amount
                    })

                    aml_obj.create({
                        'analytic_account_id': False,
                        'name': "INCOME (+)",
                        'analytic_line_ids': [],
                        'tax_line_id': False,
                        'currency_id': False,
                        'credit': self.invoice_ids[0].doku_difference_amount,
                        'debit': False,
                        'amount_currency': 0,
                        'quantity': 1.0,
                        'partner_id': aml_record.partner_id.id,
                        'move_id': move.id,
                        'account_id': doku_payment_acquirer.doku_difference_account_positive.id
                        })

                _logger.info("----aml_record.debit%s :" % aml_record.debit)
            elif self.invoice_ids[0].doku_difference_amount < 0:
                _logger.info("---- doku_difference_amount < 0 ")
                if aml_record and doku_payment_acquirer:
                    aml_record.write({
                        'debit': aml_record.debit + self.invoice_ids[0].doku_difference_amount
                    })

                    aml_obj.create({
                        'analytic_account_id': False,
                        'name': "EXPENSE (-)",
                        'analytic_line_ids': [],
                        'tax_line_id': False,
                        'currency_id': False,
                        'credit': False,
                        'debit': -(self.invoice_ids[0].doku_difference_amount),
                        'amount_currency': 0,
                        'quantity': 1.0,
                        'partner_id': aml_record.partner_id.id,
                        'move_id': move.id,
                        'account_id': doku_payment_acquirer.doku_difference_account_negative.id
                    })

                    _logger.info("----aml_record.debit%s :" % aml_record.credit)


        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move
