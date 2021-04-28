# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('amount_total', 'currency_id', 'date_order', 'company_currency_id', 'group_currency_id', 'state')
    def _amount_all_group_curr(self):
        for order in self:
            comp_curr = order.company_currency_id
            group_curr = order.group_currency_id
            if order.currency_id != group_curr:
                order.amount_total_group_curr = order.currency_id._convert(order.amount_total, group_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.amount_total_group_curr = order.amount_total
            if order.currency_id != comp_curr:
                order.amount_total_comp_curr = order.currency_id._convert(order.amount_total, comp_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.amount_total_comp_curr = order.amount_total

    @api.depends('amount_tax', 'currency_id', 'date_order', 'company_currency_id', 'group_currency_id', 'state')
    def _amount_taxed_group_curr(self):
        for order in self:
            comp_curr = order.company_currency_id
            group_curr = order.group_currency_id
            if order.currency_id != group_curr:
                order.taxed_amount_group_curr = order.currency_id._convert(order.amount_tax, group_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.taxed_amount_group_curr = order.amount_tax
            if order.currency_id != comp_curr:
                order.taxed_amount_comp_curr = order.currency_id._convert(order.amount_tax, comp_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.taxed_amount_comp_curr = order.amount_tax

    @api.depends('amount_untaxed', 'currency_id', 'date_order', 'company_currency_id', 'group_currency_id', 'state')
    def _amount_untaxed_group_curr(self):
        for order in self:
            comp_curr = order.company_currency_id
            group_curr = order.group_currency_id
            if order.currency_id != group_curr:
                order.untaxed_amount_group_curr = order.currency_id._convert(order.amount_untaxed, group_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.untaxed_amount_group_curr = order.amount_untaxed
            if order.currency_id != comp_curr:
                order.untaxed_amount_comp_curr = order.currency_id._convert(order.amount_untaxed, comp_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.untaxed_amount_comp_curr = order.amount_untaxed

    @api.depends('amount_total', 'date_order', 'state', 'order_line.invoice_lines', 'order_line.invoice_lines.invoice_id.state', 'order_line.invoice_lines.invoice_id.refund_invoice_ids.state')
    def _total_uninvoice(self):
        for order in self:
            comp_curr = order.company_currency_id
            group_curr = order.group_currency_id
            temp = 0.0
            for invoice_id in order.invoice_ids:
                if invoice_id.state not in ('draft', 'cancel'):
                    if invoice_id.type == 'out_invoice':
                        temp += invoice_id.amount_total
                    elif invoice_id.type == 'out_refund':
                        temp -= invoice_id.amount_total
            order.total_uninvoice = order.amount_total - temp
            if order.currency_id != group_curr:
                order.total_uninvoice_group_curr = order.currency_id._convert(order.total_uninvoice, group_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.total_uninvoice_group_curr = order.total_uninvoice
            if order.currency_id != comp_curr:
                order.total_uninvoice_comp_curr = order.currency_id._convert(order.total_uninvoice, comp_curr, order.company_id, order.date_order or fields.Date.today())
            else:
                order.total_uninvoice_comp_curr = order.total_uninvoice

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    total_uninvoice = fields.Monetary(
        compute='_total_uninvoice',
        string='Total Uninvoice',
        help="The total uninvoice.",
        store=True,
    )

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    untaxed_amount_group_curr = fields.Monetary(
        compute='_amount_untaxed_group_curr',
        string='IFRS Untaxed',
        help="The untaxed amount in IFRS Curr.",
        store=True
    )
    taxed_amount_group_curr = fields.Monetary(
        compute='_amount_taxed_group_curr',
        string='IFRS Tax',
        help="The taxed amount in IFRS Curr.",
        store=True
    )
    amount_total_group_curr = fields.Monetary(
        compute='_amount_all_group_curr',
        string='IFRS Total',
        help="The total amount in IFRS Curr.",
        currency_field='group_currency_id',
        store=True
    )
    total_uninvoice_group_curr = fields.Monetary(
        compute='_total_uninvoice',
        string='IFRS Uninvoice',
        help="The total uninvoice in IFRS.",
        currency_field='group_currency_id',
        store=True,
    )

    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        track_visibility='always',
        store=True,
        related='company_id.currency_id',
    )
    untaxed_amount_comp_curr = fields.Monetary(
        compute='_amount_untaxed_group_curr',
        string='Company Untaxed Ammount',
        help="The untaxed amount in Group Curr.",
        store=True
    )
    taxed_amount_comp_curr = fields.Monetary(
        compute='_amount_taxed_group_curr',
        string='Company Tax',
        help="The untaxed amount in Group Curr.",
        store=True
    )
    amount_total_comp_curr = fields.Monetary(
        compute='_amount_all_group_curr',
        string='Company Total',
        help="The total amount in Group Curr.",
        currency_field='company_currency_id',
        store=True
    )
    total_uninvoice_comp_curr = fields.Monetary(
        compute='_total_uninvoice',
        string='Company Uninvoice',
        help="The total uninvoice in company currency.",
        currency_field='company_currency_id',
        store=True,
    )

# end of sale_order()
