# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        for po in self:
            res = po.validate_po_credit_limit()
            if res:
                return res
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def validate_po_credit_limit(self):
        # check if no customer is set, or customer is not to validate
        if not self.partner_id or \
            not self.partner_id.fal_is_applied_credit_limit or \
            self.partner_id.fal_sale_warning_type != 'percentage':
            return False

        po_confirmed = self.get_po_amount()
        so_paid_amount = self.get_so_amount()
        account_receivable = self.partner_id.credit
        
        # AR + confirmed PO - paid amount
        computed_credit = (account_receivable + po_confirmed - so_paid_amount)

        restrict_margin = ((1 + (self.partner_id.fal_limit_restrict_margin / 100)) * (computed_credit))
        warning_margin = (((1 - (self.partner_id.fal_limit_warning_margin / 100)) * (self.partner_id.credit_limit)))
        # when the credit limit is reached, Block the related PO
        if self.partner_id.credit_limit <= restrict_margin:
            raise UserError(_('Can\'t confirm purchase because supplier credit limit is reached.'))
        # If the remaining credit limit is warning margin, give a warning to confirm any PO. 
        elif warning_margin <= computed_credit:
            remaining_credit = (self.partner_id.credit_limit - computed_credit)
            # showing Warning pop up if remaining credit less than warning margin
            context = dict(self._context or {})
            if context.get('force_confirm'):
                return False

            alert_wizard_obj = self.env['fal.alert.wizard']
            wizard_id = alert_wizard_obj.create({
                'purchase_order_id': self.id,
                'message': (_("Remaining credit is almost over. Confirm to continue the confirmation."))
            })

            view = self.env.ref('fal_credit_limit_formula.view_fal_alert_wizard')
            return {
                'name': _('Purchase Confirmation'),
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
        # search for related purchase for the customer
        purchase_ids = self.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'purchase')])

        # po_confirmed = sum(data.amount_total for data in purchase_ids)
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
        po_confirmed += self.amount_total
        return po_confirmed

    @api.multi
    def get_so_amount(self):
        sale_order_obj = self.env['sale.order']
        so_paid_amount = 0
        # so_paid_amount = total invoices amount - to pay amount
        # Count total SO Paid amount (convert total credit value to partner currency_id)
        invoice_paid_amount_ids = sale_order_obj.search([('partner_id', '=', self.partner_id.id)])
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
