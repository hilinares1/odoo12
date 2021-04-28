# -*- coding: utf-8 -*-
from odoo import fields, models, api
import datetime
import odoo.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('account.move.line')
    def _get_payment_ids_fal(self):
        result = {}
        for move in self:
            result[move.invoice_id.id] = True
        return result.keys()

    @api.multi
    @api.depends('payment_ids')
    def _get_effective_payment_dates(self):
        for invoice in self:
            temp = []
            for payment in invoice.payment_ids:
                temp.append(fields.Datetime.to_string(payment.payment_date))
        invoice.fal_effective_payment_dates = ";".join(temp)

    final_quotation_number = fields.Char(string='Final Quotation Number', size=64)
    fal_title = fields.Char("Title", track_visibility='onchange')
    fal_attachment = fields.Binary(string='Invoice Attachment')
    fal_attachment_name = fields.Char(string='Attachment name')
    fal_partner_contact_person_id = fields.Many2one(
        'res.partner',
        'Contact Person'
    )
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide\
        the Invoice without removing it.")

    fal_client_order_ref = fields.Char(
        'Customer PO Number', size=64,
        readonly=True, index=True
    )
    fal_quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True
    )
    fal_risk_level = fields.Integer(
        string='Risk Level',
        size=1,
        help="Risk Level define in number 1 - 9"
    )
    fal_risk_level_name = fields.Char(
        'Risk Level Name',
        size=64,
        help="Risk Level Name"
    )
    fal_effective_payment_dates = fields.Char(
        compute='_get_effective_payment_dates',
        string='Effective Payment Dates',
        help="The efective payment dates.",
        store=True
    )
    fal_use_late_payment_statement = fields.Boolean(
        'Use late payment statement', default=lambda self:
        self.env['res.users'].browse(self._uid).company_id.fal_company_late_payment_statement
    )
    fal_company_code = fields.Char(
        related='company_id.company_registry',
        string='Company Code'
    )
    fal_use_annex = fields.Boolean(
        'Use Timesheet in Annex'
    )
    fal_sale_id = fields.Many2one(
        'sale.order',
        string='Sales Source',
        compute='_fal_get_so_line',
        readonly=True
    )
    fal_timesheet_line_ids = fields.Many2many(
        'account.analytic.line',
        'analytic_timesheet_rel',
        'invoice_id',
        'fal_timesheet_line_id',
        string='Timesheet Line',
    )

    @api.depends(
        'invoice_line_ids',
        'invoice_line_ids.sale_line_ids',
        'invoice_line_ids.sale_line_ids.order_id'
    )
    def _fal_get_so_line(self):
        for line in self:
            for order_line in line.invoice_line_ids:
                for sale_order_line in order_line.sale_line_ids:
                    if sale_order_line.order_id:
                        line.fal_sale_id = sale_order_line.order_id

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(account_invoice, self).\
            _onchange_partner_id()
        partner = self.partner_id
        self.fal_partner_contact_person_id = partner.child_ids and\
            partner.child_ids[0].id or False
        return res

    @api.multi
    def _get_total_ordered_amount(self):
        for invoice in self:
            total = 0
            sale_ids = []
            purchase_ids = []
            for invoice_line in invoice.invoice_line_ids:
                if invoice.type in ['out_invoice', 'out_refund']:
                    for sale_line in invoice_line.sale_line_ids:
                        if sale_line.order_id not in sale_ids:
                            sale_ids.append(sale_line.order_id)
                            for sale in sale_ids:
                                total += sale.amount_untaxed
                elif invoice.type in ['in_invoice', 'in_refund']:
                    for purchase_line in invoice_line.purchase_line_id:
                        if purchase_line.order_id not in purchase_ids:
                            purchase_ids.append(purchase_line.order_id)
                            for purchase in purchase_ids:
                                total += purchase.amount_untaxed
            invoice.fal_total_ordered_amount = total

    @api.multi
    def _get_total_invoiced_amount(self):
        for invoice in self:
            total = 0
            invoice_list = []
            for invoice_line in invoice.invoice_line_ids:
                if invoice.type in ['out_invoice', 'out_refund']:
                    for sale_line in invoice_line.sale_line_ids:
                        for inv in sale_line.order_id.invoice_ids:
                            if inv not in invoice_list and inv.state != 'cancel':
                                invoice_list.append(inv)
                elif invoice.type in ['in_invoice', 'in_refund']:
                    for purchase_line in invoice_line.purchase_line_id:
                        for inv in purchase_line.order_id.invoice_ids:
                            if inv not in invoice_list and inv.state != 'cancel':
                                invoice_list.append(inv)
            for item in invoice_list:
                total += item.amount_untaxed if item.type in ['out_invoice', 'in_invoice'] else -item.amount_untaxed
            invoice.fal_total_amount_already_invoced = total

    @api.multi
    def _get_percentage_invoiced_ordered(self):
        for invoice in self:
            if invoice.fal_total_ordered_amount:
                invoice.fal_percentage_invoiced_ordered = \
                    invoice.fal_total_amount_already_invoced /\
                    invoice.fal_total_ordered_amount * 100

    fal_total_ordered_amount = fields.Monetary(
        'Total ordered amount', compute="_get_total_ordered_amount")
    fal_total_amount_already_invoced = fields.Monetary(
        'Total invoiced amount', compute="_get_total_invoiced_amount")
    fal_percentage_invoiced_ordered = fields.Float(
        '%invoiced / ordered', compute="_get_percentage_invoiced_ordered")

    @api.multi
    def _get_report_base_filename(self):
        res = super(account_invoice, self)._get_report_base_filename()
        if self.fal_title:
            res = res + ' - ' + self.fal_title
        return res

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.final_quotation_number:
            self.final_quotation_number = self.purchase_id.quotation_number or self.purchase_id.name
        if not self.purchase_id:
            return {}
        if not self.final_quotation_number:
            self.final_quotation_number = self.purchase_id.quotation_number or self.purchase_id.name
        if not self.fal_title:
            self.fal_title = self.purchase_id.fal_title
        res = super(account_invoice, self).purchase_order_change()
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    price_subtotal_vat = fields.Monetary(string='Subtotal with VAT', compute='_amount_line_vat', store=True)

    fal_status = fields.Selection(
        related="invoice_id.state",
        store=True,
        readonly=True
    )

    @api.multi
    @api.depends('price_unit', 'quantity', 'invoice_line_tax_ids', 'discount', 'invoice_id')
    def _amount_line_vat(self):
        for line in self:
            if line.name:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.invoice_line_tax_ids.compute_all(price, line.invoice_id.currency_id, line.quantity, line.product_id, line.invoice_id.partner_id)
                line.price_subtotal_vat = taxes['total_included']
            else:
                line.price_subtotal_vat = 0
