# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class FalRegisterDeliveryBatch(models.TransientModel):
    _name = "fal.register.delivery.batch"
    _description = "Register Delivery Batch"

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        context = self._context or {}
        res = super(FalRegisterDeliveryBatch, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if context.get('active_model', '') == 'account.invoice':
            invoices = self.env['account.invoice'].browse(context['active_ids'])
            for inv in invoices:
                if inv['state'] == 'cancel':
                    raise Warning(
                        _('At least one of the selected invoices is %s!') %
                        inv['state'])
                if inv['currency_id'] != invoices[0]['currency_id']:
                    raise Warning(
                        _('Cannot Register Delivery Batch for different Currency!'))
                if inv['partner_id'] != invoices[0]['partner_id']:
                    raise Warning(
                        _('Cannot Register Delivery Batch for different Partner!'))
        return res

    @api.model
    def _get_invoice_line_ids(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        temp = []
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            for invoice_line in invoice_id.invoice_line_ids:
                temp.append((0, 0, {
                    'invoice_line_id': invoice_line.id,
                    'product_id': invoice_line.product_id.id,
                    'name': invoice_line.name,
                    'quantity': invoice_line.quantity,
                    'uom_id': invoice_line.uom_id.id,
                    'price_unit': invoice_line.price_unit,
                }))
        return temp

    # get first partner
    @api.model
    def _get_partner(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        partner_id = []
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            partner_id.append(invoice_id.partner_id)
        return partner_id

    @api.model
    def _get_currency(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        currency_id = []
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            currency_id.append(invoice_id.currency_id)
        return currency_id

    @api.model
    def _get_payment_term(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        payment_term = []
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            payment_term.append(invoice_id.payment_term_id)
        return payment_term

    @api.multi
    def _generate_invoice_number(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        invoice_number = []
        separator = ' + '
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            invoice_number.append(invoice_id.number or 'No Invoice Number')
            final_invoice_number = separator.join(invoice_number)
        return final_invoice_number

    @api.multi
    def _generate_contract_number(self):
        context = dict(self._context or {})
        invoice_object = self.env['account.invoice']
        contract_number = []
        separator = ' + '
        for invoice_id in invoice_object.browse(context.get('active_ids')):
            contract_number.append(invoice_id.origin or 'No Source Document')
            final_contract_number = separator.join(contract_number)
        return final_contract_number

    @api.multi
    def register_delivery_batch(self):
        batch_line_temp = self._get_invoice_line_ids()
        invoice_number = self._generate_invoice_number()
        contract_number = self._generate_contract_number()
        partner = self._get_partner()
        currency = self._get_currency()
        term = self._get_payment_term()
        batch_id = self.env['fal.delivery.batch'].create({
            'number': self.env['ir.sequence'].next_by_code('delivery.batch') or '/',
            'invoice_number': invoice_number,
            'contract_number': contract_number,
            'batch_line_ids': batch_line_temp,
            'partner_id': partner[0].id,
            'currency_id': currency[0].id,
            'payment_term_id': term[0].id,
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fal.delivery.batch',
            'view_type': 'form',
            'view_mode': 'form',
            'name': 'Fal Delivery Batch',
            'res_id': batch_id.id,
        }
