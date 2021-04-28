from odoo import fields, models, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    name = fields.Char(readonly=True, copy=False)
    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="BANK Destination")
    due_date = fields.Date(string="Due date")
    is_provision = fields.Boolean(string="Is Provision?")

    _sql_constraints = [
        (
            'provision_uniq',
            'unique(fal_bank_provision_id)',
            'Bank Provision must be Unique!'),
    ]

    @api.multi
    def write(self, vals):
        result = super(AccountPayment, self).write(vals)
        # Mark a bank provision as reconciled if payment is reconciled
        for rec in self:
            if vals.get('state') and rec.fal_bank_provision_id:
                prov = self.env['fal.bank.provision'].search([('name', '=', rec.fal_bank_provision_id)])
                if prov.payment_id.state == 'reconciled' and prov.state == 'draft':
                    prov.cash()
        return result

    @api.onchange('payment_method_id')
    def onchange_payment_method_id(self):
        if self.payment_method_id:
            prov = []
            provision_in = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_in')
            prov.append(provision_in.id)
            provision_out = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_out')
            prov.append(provision_out.id)
            if self.payment_method_id.id in prov:
                self.is_provision = True
            else:
                self.is_provision = False

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(AccountPayment, self)._onchange_journal()
        if self.journal_id:
            if self.payment_type == 'inbound':
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_in').id
            else:
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_out').id
        return res

    @api.multi
    def post(self):
        res = super(AccountPayment, self).post()
        inv_list = []
        for payment in self:
            if payment.invoice_ids:
                inv_list.append((6, 0, payment.invoice_ids.ids))
            else:
                inv_list = False
            prov = []
            provision_in = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_in')
            prov.append(provision_in.id)
            provision_out = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_out')
            prov.append(provision_out.id)
            if payment.payment_method_id.id in prov:
                data = {
                    'name': payment.fal_bank_provision_id,
                    'state': 'draft',
                    'partner_id': payment.partner_id.id,
                    'payment_id': payment.id,
                    'date_payment': payment.payment_date,
                    'amount': payment.amount,
                    'invoice_ids': inv_list,
                    'note': payment.communication,
                    'due_date': payment.due_date,
                    'jurnal_dest_id': payment.jurnal_dest_id.id,
                    'currency_id': payment.currency_id.id
                }
                self.env['fal.bank.provision'].create(data)
        return res

    @api.multi
    def cancel(self):
        for rec in self:
            provision_obj = self.env['fal.bank.provision']
            prov = []
            provision_in = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_in')
            prov.append(provision_in.id)
            provision_out = self.env.ref(
                'fal_payment_bank_provision.account_payment_method_bankprov_out')
            prov.append(provision_out.id)
            if rec.payment_method_id.id in prov:
                    domain = [('name', '=', self.fal_bank_provision_id)]
                    provision = provision_obj.search(domain)
                    for rec_prov in provision:
                        rec_prov.unlink()
        return super(AccountPayment, self).cancel()


class AccountJournal(models.Model):
    _inherit = "account.journal"

    fal_is_provision = fields.Boolean(
        string='Enable Bank Provision', default=False,
        help="Check this box if this to enable Bank Provision."
    )

    @api.onchange('outbound_payment_method_ids', 'inbound_payment_method_ids')
    def _onchange_payment_method_ids(self):
        domain = {
            'default_debit_account_id': [('deprecated', '=', False)],
            'default_credit_account_id': [('deprecated', '=', False)]
        }
        if self.env.ref('fal_payment_bank_provision.account_payment_method_bankprov_in') in self.inbound_payment_method_ids or self.env.ref('fal_payment_bank_provision.account_payment_method_bankprov_out') in self.outbound_payment_method_ids:
            self.fal_is_provision = True
            domain.update({
                'default_debit_account_id': [('user_type_id', '=', self.env.ref('account.data_account_type_current_assets').id), ('deprecated', '=', False)],
                'default_credit_account_id': [('user_type_id', '=', self.env.ref('account.data_account_type_current_assets').id), ('deprecated', '=', False)]})
        else:
            self.fal_is_provision = False
        return {'domain': domain}


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    bank_provision_id = fields.Many2one(
        'fal.bank.provision', string="Bank Provision")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            amount = (' | ' + '{0:,}'.format(
                record.residual)) if record.residual else ''
            origin = (' | ' + record.origin) if record.origin else ''
            number = str(record.number) + str(origin) + amount
            result.append((record.id, number))
        return result
