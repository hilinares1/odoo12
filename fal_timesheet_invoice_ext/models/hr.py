# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import time
import odoo.addons.decimal_precision as dp

import logging

_logger = logging.getLogger(__name__)


class hr_timesheet_invoice_factor(models.Model):
    _name = "hr_timesheet_invoice.factor"
    _description = "Invoice Rate"

    name = fields.Char(
        string='Internal Name',
        required=True,
        translate=True
    )
    customer_name = fields.Char(
        string='Name',
        help="Label for the customer"
    )
    factor = fields.Float(
        string='Discount (%)',
        required=True,
        help="Discount in percentage"
    )
    coef = fields.Float(
        string='Coef',
        required=True,
        help="For timesheet calc"
    )

# end of hr_timesheet_invoice_factor()


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    to_invoice = fields.Many2one(
        'hr_timesheet_invoice.factor',
        'Timesheet Invoicing Ratio',
        help="You usually invoice 100% of the timesheets. \
        But if you mix fixed price and timesheet invoicing, \
        you may use another ratio. For instance, \
        if you do a 20% advance invoice (fixed price, based on a sales order),\
        you should invoice the rest on timesheet with a 80% ratio."
    )

# end of account_analytic_account()


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    to_invoice = fields.Many2one(
        'hr_timesheet_invoice.factor',
        'Invoiceable',
        help="It allows to set the discount while making invoice, \
        keep empty if the activities should not be invoiced.")
    unit_amount_coef = fields.Float(
        string='Coef',
        help="quantity x (1 – Coef)"
    )
    sale_line_id = fields.Many2one(
        'sale.order.line', 'Sales Order Line Item', compute='_get_sale_line')

    @api.depends('task_id', 'task_id.sale_line_id')
    def _get_sale_line(self):
        for item in self:
            item.sale_line_id = item.task_id.sale_line_id

    # quantity x (1 – Coef)
    @api.onchange('unit_amount', 'to_invoice')
    def onchange_unit_amount_coef(self):
        if self.to_invoice:
            self.unit_amount_coef = self.unit_amount \
                * (1 - self.to_invoice.coef)

    @api.onchange('account_id')
    def onchange_account_id(self):
        if self.account_id:
            self.to_invoice = self.account_id.to_invoice.id

    @api.model
    def create(self, vals):
        res = super(account_analytic_line, self).create(vals)
        if not vals.get('to_invoice', False):
            aa_obj = self.env['account.analytic.account']
            vals['to_invoice'] = aa_obj.browse(
                vals['account_id']).to_invoice.id
        return res

    @api.multi
    def write(self, vals):
        self._check_inv(vals)
        sale_order_lines = self.env['sale.order.line']
        if 'to_invoice' in vals and not vals.get('so_line'):
            sale_order_lines = self.sudo().mapped('so_line')
        result = super(account_analytic_line, self).write(vals)
        sale_order_lines.with_context(sale_analytic_force_recompute=True)._get_delivered_quantity_by_analytic([('amount', '<=', 0.0)])
        return result

    @api.multi
    def _check_inv(self, vals):
        if ('timesheet_invoice_id' not in vals and 'sheet_id' not in vals):
            for line in self:
                if (line.timesheet_invoice_id and line.sheet_id.state != 'new'):
                    raise UserError(_(
                        'You cannot modify an invoiced analytic line!'))
        return True

    @api.model
    def _prepare_timesheet_invoice(self, partner_id, company_id, currency_id):
        """ returns values used to create main invoice from analytic lines"""
        account_payment_term_obj = self.env['account.payment.term']
        invoice_name = self.account_id.name

        date_due = False
        if partner_id.property_payment_term_id:
            pterm_list = account_payment_term_obj.compute(
                value=1, date_ref=time.strftime('%Y-%m-%d'))
            if pterm_list:
                pterm_list = [line[0] for line in pterm_list]
                pterm_list.sort()
                date_due = pterm_list[-1]
        return {
            'name': "%s - %s" % (time.strftime('%d/%m/%Y'), invoice_name),
            'partner_id': partner_id.id,
            'company_id': company_id.id,
            'payment_term': partner_id.property_payment_term_id.id or False,
            'account_id': partner_id.property_account_receivable_id.id,
            'currency_id': currency_id.id,
            'date_due': date_due,
            'fiscal_position': partner_id.property_account_position_id.id
        }

# end of account_analytic_line()
