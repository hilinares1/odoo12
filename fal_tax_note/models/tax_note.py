from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
from datetime import datetime
from odoo.exceptions import UserError


class FalTaxNote(models.Model):
    _name = 'fal.tax.note'
    _description = 'Tax Note'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('tax_note_line', 'tax_note_line.amount')
    def _compute_amount(self):
        for item in self:
            amount = sum(
                (line.amount) for line in item.tax_note_line)
            item.total_tax_amount = amount

    @api.model
    def _default_start_date(self):
        date = fields.date.today()
        first_day = date + relativedelta(day=1)
        return first_day

    @api.model
    def _default_end_date(self):
        date = fields.date.today()
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        return last_day

    @api.model
    def _default_journal_id(self):
        journal = self.env['account.journal'].search(
            [('fal_is_tax_journal', '=', True)], limit=1)
        return journal.id

    @api.onchange('date_start')
    def _onchange_date(self):
        res = {}
        if self.date_start:
            date_start = self.date_start
            # date = date_start.strftime(
            #     self.date_start, '%Y-%m-%d')
            date = fields.Date.from_string(date_start)
            last_day = date + relativedelta(day=1, months=+1, days=-1)
            self.date_end = last_day
            return res

    name = fields.Char(
        required=1, readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        required=True, readonly=True, states={'draft': [('readonly', False)]}
    )
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', required=True,
        readonly=True, states={'draft': [('readonly', False)]}
    )
    user_id = fields.Many2one(
        'res.users', string="Responsible",
        default=lambda self: self.env.user,
        readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True,
        readonly=True, states={'draft': [('readonly', False)]}
    )
    date_start = fields.Date(
        string='Start Date', default=_default_start_date,
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Date(
        string='Ending Date', default=_default_end_date,
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled'),
    ], string='State', default='draft')
    journal_id = fields.Many2one(
        'account.journal', string='Journal', required=1,
        readonly=True, states={'draft': [('readonly', False)]},
        default=_default_journal_id)
    move_id = fields.Many2one(
        'account.move', string='Journal Entries',
        states={'draft': [('readonly', False)]})
    payment_id = fields.Many2one(
        'account.payment', string='Payment',
        states={'draft': [('readonly', False)]})

    tax_note_line = fields.One2many(
        'fal.tax.note.line', 'tax_note_id', string="Tax Note Line",
        readonly=True, states={'draft': [('readonly', False)]}
    )
    total_tax_amount = fields.Float(compute=_compute_amount)
    tax_payment = fields.Boolean(string='Tax Payment')
    fal_attachment = fields.Binary(
        string='Related Attachment', attachment=True, filestore=True, 
        help="You can put related file attachment here")
    fal_attachment_name = fields.Char(
        string='Attachment Name',
        help="You can put related file attachment here")

    @api.multi
    def action_confirm(self):
        for tax_note in self:
            if not tax_note.tax_note_line:
                raise UserError(_('Please Select Tax'))
            tax_note.write({'state': 'confirm'})

    @api.multi
    def action_select(self):
        context = {
            'default_date_start': self.date_start,
            'default_date_end': self.date_end,
        }
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'res_model': 'tax.selection.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_reconcile(self):
        return {
            'name': ('Reconcile'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'domain': [('account_id', 'in', self.tax_note_line.mapped('account_id').ids)],
        }

    @api.multi
    def action_validate(self):
        move_obj = self.env['account.move']
        for tax_note in self:
            payment_date = fields.Date.context_today(self)
            company_currency = self.company_id.currency_id
            current_currency = self.currency_id
            total_tax_amount = current_currency.compute(
                tax_note.total_tax_amount, company_currency)
            prec = self.env['decimal.precision'].precision_get('Account')

            lineas = []
            for line in tax_note.tax_note_line:
                move_line_1 = {
                    'debit': line.amount if float_compare(
                        line.amount, 0.0, precision_digits=prec
                    ) > 0 else 0.0,
                    'credit': 0.0 if float_compare(
                        line.amount, 0.0, precision_digits=prec
                    ) > 0 else -line.amount,
                    'amount_currency': line.amount,
                    'name': tax_note.name,
                    'account_id': line.account_id.id,
                    'analytic_account_id': line.analytic_account_id.id,
                    'partner_id': tax_note.partner_id.id,
                    'date': payment_date,
                    'currency_id': tax_note.currency_id.id,
                }
                lineas.append((0, 0, move_line_1))

            move_line_2 = {
                'debit': 0.0 if float_compare(
                    total_tax_amount, 0.0, precision_digits=prec
                ) > 0 else -total_tax_amount,
                'credit': 0.0 if float_compare(
                    total_tax_amount, 0.0, precision_digits=prec
                ) < 0 else total_tax_amount,
                'amount_currency': -tax_note.total_tax_amount,
                'name': tax_note.name + " total tax",
                'account_id': tax_note.partner_id.property_account_receivable_id.id if total_tax_amount < 0 else tax_note.partner_id.property_account_payable_id.id,
                'partner_id': tax_note.partner_id.id,
                'date': payment_date,
                'currency_id': tax_note.currency_id.id,
            }

            lineas.append((0, 0, move_line_2))

            move_vals = {
                'ref': tax_note.name,
                'date': payment_date,
                'journal_id': tax_note.journal_id.id,
                'line_ids': lineas,
            }
            move = move_obj.create(move_vals)
            move.post()

            for tax_line in tax_note.tax_note_line:
                tax_line.move_line_id.write({
                    'fal_reported': True,
                })
            tax_note.write({'state': 'validate', 'move_id': move.id})

    @api.multi
    def action_draft(self):
        for tax_note in self:
            tax_note.write({'state': 'draft'})

    def action_register(self):
        amount = self.total_tax_amount
        context = {
            'default_amount': abs(amount),
            'default_payment_type': 'inbound' if amount < 0 else 'outbound',
            'default_partner_type': 'customer' if amount < 0 else 'supplier',
            'default_communication': self.name,
        }
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.register.payments',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_cancel(self):
        for tax_note in self:
            tax_note.write({'state': 'cancel'})

    @api.multi
    def _get_aml_for_register_payment(self):
        """ Get the aml to consider to reconcile in register payment """
        self.ensure_one()
        return self.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        """ Reconcile payable/receivable lines from the invoice with payment_line """
        line_to_reconcile = self.env['account.move.line']
        for tax_note in self:
            line_to_reconcile += tax_note._get_aml_for_register_payment()
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)


class FalTaxNoteLine(models.Model):
    _name = 'fal.tax.note.line'
    _description = 'Tax Note Line'

    tax_note_id = fields.Many2one('fal.tax.note')
    product_id = fields.Many2one('product.product', string="Product")
    name = fields.Char(string="Label")
    invoice_id = fields.Many2one(
        'account.invoice', string="Invoice")
    move_line_id = fields.Many2one('account.move.line', string="Move Line")
    account_id = fields.Many2one(
        'account.account', string="Account", required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True)
    tax_line_id = fields.Many2one('account.tax', string="Originator Tax")
    number = fields.Char('Reference')
    untaxed_amount = fields.Float(string="Untaxed Amount")
    amount = fields.Float(string="Amount")
    amount_total = fields.Float(string="Amount Total")
