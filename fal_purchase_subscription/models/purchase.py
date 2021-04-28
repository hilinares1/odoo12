# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fal_purchase_subscription_id = fields.Many2one('fal.purchase.subscription', 'Subscription')

    def purchase_subscription(self):
        starting_date = self.date_order
        context = {
            'default_starting_date': starting_date,
            'default_name': _('Subs ') + self.name
        }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Purchase Subscription'),
            'res_model': 'fal.purchase.subscription.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': context
        }


class PurchaseSubscription(models.Model):
    _name = 'fal.purchase.subscription'
    _description = 'Purchase Subscription'

    name = fields.Char("Name")
    purchase_order = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        readonly=True
    )
    starting_date = fields.Date(required=True, default="")
    next_date = fields.Date(required=True, default="")
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
    active = fields.Boolean(default=True)

    @api.model
    def _cron_recurring_create_purchase(self):
        return self._recurring_create_purchase(automatic=True)

    @api.multi
    def recurring_rfq(self):
        self._recurring_create_purchase()

    @api.returns('fal.purchase.subscription')
    def _recurring_create_purchase(self, automatic=False):
        date_today = fields.Date.today()
        periods = {
            'days': 'days',
            'weeks': 'weeks',
            'months': 'months',
            'years': 'years'
        }
        for purchase_subscription in self.search([
                ('next_date', '<=', date_today),('active', '=', True)]):
            copy_po = purchase_subscription.purchase_order.copy()
            copy_po.write({
                'date_order': purchase_subscription.next_date,
                'date_planned': purchase_subscription.next_date
            })
            next_date = fields.Date.from_string(
                purchase_subscription.next_date)
            rule, interval = purchase_subscription.interval_unit, purchase_subscription.interval
            new_date = next_date + relativedelta(**{periods[rule]: interval})
            purchase_subscription.next_date = new_date
