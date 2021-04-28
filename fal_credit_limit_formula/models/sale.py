# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_propose(self):
        for so in self:
            res = so.validate_so_credit_limit()
            if res:
                return res
        return super(SaleOrder, self).action_propose()

    @api.multi
    def validate_so_credit_limit(self):
        # check if no customer is set, or customer is not to validate
        if not self.partner_id or \
            not self.partner_id.fal_is_applied_credit_limit or \
            self.partner_id.fal_sale_warning_type != 'percentage':
            return False

        po_confirmed = self.get_po_amount()
        so_paid_amount = self.get_so_amount()
        account_receivable = self.partner_id.credit

        # AR + confirmed PO + current SO total amount - paid amount
        computed_credit = (account_receivable + po_confirmed + self.amount_total - so_paid_amount)

        restrict_margin = ((1 + (self.partner_id.fal_limit_restrict_margin / 100)) * (computed_credit))
        warning_margin = (((1 - (self.partner_id.fal_limit_warning_margin / 100)) * (self.partner_id.credit_limit)))
        # when the credit limit is reached, Block the related SO
        if self.partner_id.credit_limit <= restrict_margin:
            raise UserError(_("Can not propose order due to customer credit limit."))
        # If the remaining credit limit is less than warning margin give a warning.
        elif warning_margin <= computed_credit:
            remaining_credit = (self.partner_id.credit_limit - computed_credit)
            # showing Warning pop up if remaining credit less than warning margin
            context = dict(self._context or {})
            if context.get('sale_force_confirm'):
                return False

            alert_wizard_obj = self.env['fal.alert.wizard']
            wizard_id = alert_wizard_obj.create({
                'sale_order_id': self.id,
                'message': (_("Remaining credit is almost over. Confirm to continue or cancel."))
            })
            # showing wizard form view
            view = self.env.ref('fal_credit_limit_formula.view_fal_alert_wizard')
            return {
                'name': _('Sales Confirmation'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fal.alert.wizard',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wizard_id.id
            }
        return False

    @api.multi
    def get_po_amount(self):
        po_confirmed = 0
        purchase_order_obj = self.env['purchase.order']
        purchase_ids = purchase_order_obj.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'purchase')])

        # Count total PO confirmed (convert total credit value to partner currency_id)
        for order in purchase_ids:
            if order.currency_id != self.partner_id.partner_currency_id:
                po_confirmed_converted = order.currency_id._convert(
                    order.amount_total,
                    self.partner_id.partner_currency_id,
                    order.company_id,
                    order.date_order
                )
                po_confirmed += po_confirmed_converted
            else:
                po_confirmed += order.amount_total
        return po_confirmed

    @api.multi
    def get_so_amount(self):
        so_paid_amount = 0
        # so_paid_amount = total invoices amount - to pay amount
        # Count total SO Paid amount (convert total credit value to partner currency_id)
        invoice_paid_amount_ids = self.search([('partner_id', '=', self.partner_id.id)])
        for data in invoice_paid_amount_ids:
            record_invoice_ids = data.invoice_ids
            total_amount_temp = 0
            for record in record_invoice_ids:
                total = record.amount_total_signed
                to_pay = record.residual_signed
                paid_amount = total - to_pay
                total_amount_temp += paid_amount

                if record.currency_id != self.partner_id.partner_currency_id:
                    so_paid_amount_converted = record.currency_id._convert(
                        total_amount_temp,
                        self.partner_id.partner_currency_id,
                        record.company_id,
                        record.date_invoice or fields.Date.today()
                    )
                    so_paid_amount += so_paid_amount_converted
                else:
                    so_paid_amount += total_amount_temp
        return so_paid_amount
