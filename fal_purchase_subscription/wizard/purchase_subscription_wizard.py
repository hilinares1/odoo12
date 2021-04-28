# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class FalPurchaseSubcriptionWizard(models.TransientModel):
    _name = "fal.purchase.subscription.wizard"
    _description = "Falinwa Purchase Subscription Wizard"

    name = fields.Char("Name")
    purchase_order = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True
    )
    starting_date = fields.Date(string='Starting Date', readonly=True)
    next_date = fields.Date(string='Next Date', required=True)
    interval = fields.Integer(
        string='Interval', default=1,
        help="Interval in time units")
    interval_unit = fields.Selection(
        selection=[('days', 'days'),
                   ('weeks', 'weeks'),
                   ('months', 'months'),
                   ('years', 'years')],
        string='Interval unit', default='years',
        help='Time unit for the interval')

    @api.onchange('interval_unit', 'interval')
    def _onchange_interval(self):
        periods = {
            'days': 'days',
            'weeks': 'weeks',
            'months': 'months',
            'years': 'years'
        }
        if self.interval:
            next_date = fields.Date.from_string(
                self.starting_date)
            rule, interval = self.interval_unit, \
                self.interval
            new_date = next_date + relativedelta(
                **{periods[rule]: interval})
            self.next_date = new_date

    def generate_purchase_subscription(self):
        if self._context.get('active_id'):
            active_po = self.env['purchase.order'].browse(self._context.get('active_id'))
            purchase_subscription = self.env['fal.purchase.subscription'].create(
                {
                    'name': self.name,
                    'purchase_order': active_po.id,
                    'interval': self.interval,
                    'interval_unit': self.interval_unit,
                    'starting_date': active_po.date_order,
                    'next_date': self.next_date,
                }
            )
            active_po.fal_purchase_subscription_id = purchase_subscription

        return True
