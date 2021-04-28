# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = "crm.lead"

    company_currency = fields.Many2one('res.currency', string='Currency', compute='_get_company_currency', related='', readonly=True)

    @api.multi
    @api.depends('company_id')
    def _get_company_currency(self):
        for record in self:
            company_id = record.company_id 
            if not company_id:
                record.company_currency = self.env.user.company_id.group_currency_id.id
            else:
                record.company_currency = company_id.currency_id

    @api.depends(
        'group_currency_id', 'company_currency',
        'planned_revenue', 'date_open', 'state_id')
    def _amount_all_group_curr(self):
        amount_total = 0.0
        for order in self:

            rate_ids = order.group_currency_id
            company = order.company_id or self.env.user.company_id

            if order.company_currency != rate_ids:
                amount_total = order.company_currency._convert(
                    order.planned_revenue,
                    rate_ids,
                    company,
                    order.date_open or fields.Date.today()
                )
            else:
                amount_total = order.planned_revenue
            order.amount_total_group_curr = amount_total

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for invoice in self:
            company_id = invoice.company_id 
            if not company_id:
                company_id = self.env.user.company_id

            invoice.group_currency_id = company_id.group_currency_id

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    amount_total_group_curr = fields.Monetary(
        compute='_amount_all_group_curr',
        string='IFRS Expected Revenue',
        currency_field='group_currency_id',
        store=True
    )

    # show amount in current company currency
    @api.depends('curr_company_id')
    def _amount_company_currency(self):
        for order in self:
            amount_total = order.planned_revenue
            curr = self.env.user.company_id.currency_id
            company = order.company_id or self.env.user.company_id
            if order.company_currency != curr:
                amount_total = order.company_currency._convert(
                    order.planned_revenue,
                    curr,
                    company,
                    order.date_open or fields.Date.today()
                )
            order.amount_company_currency = amount_total

    def _cur_company_id(self):
        for order in self:
            company_id = order.company_id
            if not company_id:
                order.curr_company_id = self.env.user.company_id.group_currency_id
            else:
                curr = self.env.user.company_id.currency_id.id
                order.curr_company_id = curr

    curr_company_id = fields.Many2one(
        'res.currency', string='Currency', index=True, compute='_cur_company_id')

    amount_company_currency = fields.Monetary(
        compute='_amount_company_currency',
        string='Company Currency',
        currency_field='curr_company_id',
    )
# end of sale_order()
