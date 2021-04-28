# -*- encoding: utf-8 -*-

import logging
from datetime import date, datetime
from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # completly override odoo method
    @api.one
    def asset_create(self):
        for data in range(int(self.quantity)):
            if self.asset_category_id:
                vals = {
                    'name': self.name,
                    'code': self.invoice_id.number or False,
                    'category_id': self.asset_category_id.id,
                    'value': self.price_subtotal_signed / self.quantity,
                    'partner_id': self.invoice_id.partner_id.id,
                    'company_id': self.invoice_id.company_id.id,
                    'currency_id': self.invoice_id.company_currency_id.id,
                    'date': self.invoice_id.date_invoice,
                    'invoice_id': self.invoice_id.id,
                    # Change start here
                    'fal_purchase_date': self.asset_start_date,
                    'fal_original_purchase_value': self.price_subtotal_signed / self.quantity,
                    # End here
                }
                changed_vals = self.env['account.asset.asset'].onchange_category_id_values(vals['category_id'])
                vals.update(changed_vals['value'])
                asset = self.env['account.asset.asset'].create(vals)
                if self.asset_category_id.open_asset:
                    # Change start here
                    # If it's manual our field should be filled, else it will lock
                    # On running, can't be drafted because field are empty but required
                    if asset.date_first_depreciation == 'manual':
                        asset.first_depreciation_manual_date = self.invoice_id.date_invoice
                    # End here
                    asset.validate()
        return True


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_asset_ids = fields.One2many(
        'account.asset.asset', 'invoice_id', 'Assets')
    fal_asset_count = fields.Integer(
        compute='_compute_fal_asset_count', string='Asset Count')

    @api.multi
    def _compute_fal_asset_count(self):
        for invoice in self:
            invoice.fal_asset_count = len(invoice.fal_asset_ids)

    @api.multi
    def open_fal_asset(self):
        return {
            'name': _('Assets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.asset.asset',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': dict(
                self.env.context or {},
                default_type='purchase',
                search_default_invoice_id=self.id,
                default_invoice_id=self.id),
        }
