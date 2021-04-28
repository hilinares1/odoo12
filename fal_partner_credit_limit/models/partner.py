# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

position = [
    (1, 'Position 0'),
    (2, 'Position 1'),
    (3, 'Position 2'),
    (4, 'Position 3'),
    (5, 'Position 4'),
]


class Partner(models.Model):
    _inherit = 'res.partner'

    fal_sale_warning_type = fields.Selection([
        ('none', 'None'),
        ('blocked', 'Block'),
        ('value', 'Value'),
        ('days', 'Delay on overdue'),
        ('valuedate', 'Value And Delay on overdue')
    ], default='none', string='Sale Restriction')
    fal_remaining_credit_limit = fields.Float(
        string="Remaining Credit limit",
        compute='_compute_remaining_credit_limit')
    fal_oldest_invoice_no = fields.Many2one(
        'account.invoice',
        string="Oldest invoice no",
        compute='_compute_get_oldest_invoice')
    fal_oldest_invoice_age = fields.Integer(
        string='Oldest invoice age', compute='_compute_get_oldest_invoice')
    fal_deptor_position = fields.Selection(
        position,
        string='Debtor position',
        compute='_compute_get_position'
    )
    fal_block_level = fields.Selection(
        position,
        string='Block Level',
    )

    @api.multi
    @api.depends('credit_limit', 'credit')
    def _compute_remaining_credit_limit(self):
        for item in self:
            item.fal_remaining_credit_limit = item.credit_limit - item.credit

    def _compute_get_oldest_invoice(self):
        today = fields.Date.today()
        for item in self:
            inv = self.env['account.invoice'].search([
                ('partner_id', '=', item.id)],
                order="date_invoice,id asc", limit=1)
            item.fal_oldest_invoice_no = inv.id
            duration = 0
            if inv.date_due and inv.state != 'paid':
                duration = float((today - inv.date_due).days)
                if duration < 0:
                    item.fal_oldest_invoice_age = 0
                else:
                    item.fal_oldest_invoice_age = duration

    @api.depends('fal_oldest_invoice_age', 'credit')
    def _compute_get_position(self):
        for item in self:
            if item.credit > 0:
                if item.fal_oldest_invoice_age <= 0:
                    item.fal_deptor_position = 1
                elif item.fal_oldest_invoice_age > 0 and item.fal_oldest_invoice_age <= 30:
                    item.fal_deptor_position = 2
                elif item.fal_oldest_invoice_age > 30 and item.fal_oldest_invoice_age <= 60:
                    item.fal_deptor_position = 3
                elif item.fal_oldest_invoice_age > 60 and item.fal_oldest_invoice_age <= 90:
                    item.fal_deptor_position = 4
                elif item.fal_oldest_invoice_age > 90:
                    item.fal_deptor_position = 5
