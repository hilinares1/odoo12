# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    jurnal_dest_id = fields.Many2one(
        'account.journal',
        string="BANK Destination")
    due_date = fields.Date(string="Due date")
    is_provision = fields.Boolean(string="Is Provision?")

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(account_register_payments, self)._onchange_journal()
        if self.journal_id:
            if self.payment_type == 'inbound':
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_in').id
            else:
                self.payment_method_id = self.env.ref(
                    'account.account_payment_method_manual_out').id
        return res

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(account_register_payments, self)._prepare_payment_vals(invoices)
        res.update({
            'payment_method_id': self.payment_method_id.id,
            'fal_bank_provision_id': self.fal_bank_provision_id,
            'jurnal_dest_id': self.jurnal_dest_id.id,
            'due_date': self.due_date
        })
        return res

    @api.multi
    def create_payments(self):
        res = super(account_register_payments, self).create_payments()
        if self.fal_split_multi_payment:
            for line in self.payment_wizard_line_ids:
                if line.is_provision:
                    if not line.fal_bank_provision_id:
                        raise UserError('Please set No. Bank Provision')
        return res

    @api.onchange('payment_method_id')
    def _onchange_payment_method_id(self):
        res = super(account_register_payments, self)._onchange_payment_method_id()
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
        return res


class fal_multi_payment_wizard(models.TransientModel):
    _inherit = "fal.multi.payment.wizard"

    fal_bank_provision_id = fields.Char(string='No. Bank Provision')
    is_provision = fields.Boolean(
        string="Is Provision?", related="register_payments_id.is_provision")

    @api.multi
    def _prepare_payment_vals(self, invoices):
        res = super(fal_multi_payment_wizard, self)._prepare_payment_vals(invoices)
        res.update({
            'payment_method_id': self.payment_method_id.id,
            'fal_bank_provision_id': self.fal_bank_provision_id,
            'jurnal_dest_id': self.register_payments_id.jurnal_dest_id.id,
            'due_date': self.register_payments_id.due_date
        })
        return res
