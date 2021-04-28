from odoo import fields, models, api
from datetime import datetime


class BankProvision(models.Model):
    _name = 'fal.bank.provision'
    _inherit = ['mail.thread']
    _description = 'Bank Provision'

    name = fields.Char(string='No. Bank Provision')
    partner_id = fields.Many2one('res.partner', string="Customer")
    date_payment = fields.Date('Payment Date')
    amount = fields.Monetary(string='Amount')
    note = fields.Text("Note")
    state = fields.Selection([
        ('draft', 'Not Cashed'),
        ('reconcile', 'Cashed')
    ], default='draft', track_visibility='always')
    fal_bank_id = fields.Many2one(
        'res.bank', string="Issuing Bank")
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="Cashed to", domain=[('type', '=', 'bank')])
    due_date = fields.Date(string="Due date")

    Notes = fields.Char('Notes', track_visibility='always')
    date_reconciled = fields.Date(
        string="Cashed Date", track_visibility='always')

    company_id = fields.Many2one(
        'res.company', 'Company')
    payment_id = fields.Many2one(
        'account.payment', 'Payment ID')
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        default=lambda self: self.jurnal_dest_id.currency_id)
    invoice_ids = fields.Many2many(
        'account.invoice', 'fal_bank_provision_invoice_rel',
        'bank_provision_id', 'invoice_id', string="Invoices", copy=False,
        readonly=True)
    communication = fields.Char(string='Memo')
    move_id = fields.Many2one('account.move', string="Journal Entry")
    count_day = fields.Integer(
        string="Count Day", compute="_computeCountDate")

    def _computeCountDate(self):
        fmt = '%Y-%m-%d'
        for data in self:
            datenow = fields.Date.context_today(self)
            dateliquidity = data.due_date
            if dateliquidity:
                d1 = fields.Date.from_string(dateliquidity)
                d2 = fields.Date.from_string(datenow)
                # d1 = datetime.strptime(dateliquidity, fmt)
                # d2 = datetime.strptime(datenow, fmt)
                data.count_day = int((d2 - d1).days)

    @api.multi
    @api.onchange('jurnal_dest_id')
    def _chg_jurnal_dest_id(self):
        self.currency_id = self.jurnal_dest_id.currency_id.id

    @api.multi
    def cash(self):
        created_moves = self.env['account.move']
        line_list = []
        datenow = fields.Date.context_today(self)
        for line in self:
            # prec = self.env['decimal.precision'].precision_get('Account')
            name = "Provision - " + str(line.name)
            self_currency = line.currency_id
            amount = line.amount
            db_acc = line.jurnal_dest_id.default_credit_account_id.id
            cr_acc = line.payment_id.journal_id.default_debit_account_id.id

            move_line_1 = {
                'name': name,
                'account_id': db_acc or False,
                'debit': 0.0 if line.payment_id.partner_type == 'supplier' else amount,
                'credit': amount if line.payment_id.partner_type == 'supplier' else 0.0,
                'journal_id': line.jurnal_dest_id.id,
                'currency_id': self_currency.id or False,
                'amount_currency': -1 * amount if line.payment_id.partner_type == 'supplier' else amount,
                'product_uom_id': 1
            }
            line_list.append((0, 0, move_line_1))

            move_line_2 = {
                'name': name,
                'account_id': cr_acc or False,
                'debit': amount if line.payment_id.partner_type == 'supplier' else 0.0,
                'credit': 0.0 if line.payment_id.partner_type == 'supplier' else amount,
                'journal_id': line.jurnal_dest_id.id,
                'currency_id': self_currency.id or False,
                'amount_currency': amount if line.payment_id.partner_type == 'supplier' else -1 * amount,
                'product_uom_id': 1
            }
            line_list.append((0, 0, move_line_2))

        move_vals = {
            'ref': name,
            'date': datenow,
            'journal_id': self.jurnal_dest_id.id,
            'line_ids': line_list,
        }

        move = created_moves.create(move_vals)
        move.post()
        # Update State
        self.move_id = move.id
        self.state = 'reconcile'
        self.date_reconciled = datenow
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def uncash(self):
        self.move_id.button_cancel()
        self.state = 'draft'
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def set_receive(self):
        self.state = 'used'
        return {'type': 'ir.actions.act_window_close'}
