# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import netsvc
import base64
import re


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('fal_supplier_account_invoice_line_ids')
    def _get_ASI(self):
        asi_id = []
        for asi in self.fal_supplier_account_invoice_line_ids:
            if asi.invoice_id.id not in asi_id:
                asi_id.append(asi.invoice_id.id)
        self.fal_supplier_account_invoice_ids = [(6, 0, asi_id)]

    @api.one
    @api.depends(
        'price_subtotal',
        'invoice_id.amount_total',
        'fal_supplier_account_invoice_line_ids',
        'fal_supplier_account_invoice_line_ids.price_subtotal'
    )
    def _get_margin(self):
        asi_amount = 0
        for asi in self.fal_supplier_account_invoice_line_ids:
            asi_amount += asi.price_subtotal
        if self.price_subtotal:
            self.fal_margin = (self.price_subtotal - asi_amount) / self.price_subtotal
        else:
            self.fal_margin = 0

    @api.one
    @api.depends('fal_supplier_account_invoice_line_ids')
    def _get_ASI_line_display(self):
        display_name = ""
        for supplier_invoice_line in self.fal_supplier_account_invoice_line_ids:
            display_name += supplier_invoice_line.invoice_id.number + "-" + supplier_invoice_line.name + ", "
        display_name = display_name[:-2]
        self.fal_supplier_account_invoice_line_ids_display = display_name

    @api.one
    @api.depends(
        'fal_supplier_account_invoice_line_ids',
        'fal_supplier_account_invoice_line_ids.quantity'
    )
    def _get_ASI_qty(self):
        qty = 0
        for asi in self.fal_supplier_account_invoice_line_ids:
            qty += asi.quantity
        self.fal_asi_qty = qty

    @api.one
    @api.depends('fal_supplier_account_invoice_line_ids', 'fal_supplier_account_invoice_line_ids.price_subtotal')
    def _get_ASI_amount(self):
        amount = 0
        for asi in self.fal_supplier_account_invoice_line_ids:
            amount += asi.price_subtotal
        self.fal_asi_amount = amount

    fal_margin = fields.Float("Margin", compute="_get_margin")
    fal_invoice_id_date_invoice = fields.Date(
        'Invoice Date',
        related="invoice_id.date_invoice"
    )
    fal_invoice_id_state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')],
        related="invoice_id.state"
    )
    fal_account_invoice_type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund')],
        related="invoice_id.type"
    )
    fal_no_match_reason = fields.Selection([
        ('non_business_cost', 'Non-Business Costs'),
        ('aci_end_of_fy', 'ACI end of FY'),
        ('sold_on_stock', 'Sold on Stock'),
    ], string="No Match Reason", readonly=False)
    fal_mathching_ok = fields.Boolean("Match", readonly=False)
    # On Supplier
    fal_customer_account_invoice_id = fields.Many2one(
        "account.invoice",
        "ACI", help="Account Invoice",
        domain="[('type','=','out_invoice')]"
    )
    fal_customer_account_invoice_line_ids = fields.Many2many(
        "account.invoice.line",
        "supplier_aci_line_customer_aci_line_rel",
        "supplier_account_invoice_line_id",
        "customer_account_invoice_line_id",
        "ACIL",
        domain="[('invoice_id','=',fal_customer_account_invoice_id)]", help="Account Customer Invoice Line"
    )
    # On Customer
    fal_asi_amount = fields.Float(
        "ASI Amount",
        compute="_get_ASI_amount",
        store=True
    )
    fal_supplier_account_invoice_ids = fields.Many2many(
        "account.invoice",
        "supplier_aci_customer_aci_line_rel",
        "customer_account_invoice_line_id",
        "supplier_account_invoice_id",
        "ASI",
        compute="_get_ASI"
    )
    fal_asi_qty = fields.Float("ASI Qty", compute="_get_ASI_qty", store=True)
    fal_supplier_account_invoice_line_ids = fields.Many2many(
        "account.invoice.line",
        "supplier_aci_line_customer_aci_line_rel",
        "customer_account_invoice_line_id",
        "supplier_account_invoice_line_id",
        string="ASIL", help="Account Supplier Invoice Line"
    )
    fal_supplier_account_invoice_line_ids_display = fields.Char(
        "ASIL",
        compute="_get_ASI_line_display",
        store=True, help="Account Supplier Invoice Line"
    )
