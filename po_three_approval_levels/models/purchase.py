# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare

from odoo.exceptions import UserError

from odoo.addons.purchase.models.purchase import PurchaseOrder as Purchase


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approval'),
        ('manager', 'Wating Purchase Manager Approval'),
        ('accountant', 'Wating Accoutant Approval'),
        ('director', 'Wating Director Approval'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    manager_user_id = fields.Many2one('res.users', string='Approval Manager', readonly=True)
    accountant_user_id = fields.Many2one('res.users', string='Approval Accoutant', readonly=True)
    director_user_id = fields.Many2one('res.users', string='Approval Director', readonly=True)
    manager_approve_date = fields.Date('Manager Approval Date', readonly=1, index=True, copy=False)
    accountant_approve_date = fields.Date('Accoutant Approval Date', readonly=1, index=True, copy=False)
    director_approve_date = fields.Date('Director Approval Date', readonly=1, index=True, copy=False)

    #Manager Approve Button Funcion
    @api.multi
    def button_manager_approve(self, force=False):
        for order in self:
            # Deal with Three Step validation process
            if order.company_id.po_approval == True:
                if order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.manager_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()):
                    order.button_approve()
                else:
                    order.write({'state': 'accountant'})
            order.write({'manager_user_id': self.env.user.id, 'manager_approve_date': fields.Date.context_today(self)})
        return True

    #Accountant Approve Button Funcion
    @api.multi
    def button_accountant_approve(self, force=False):
        for order in self:
            # Deal with Three Step validation process
            if order.company_id.po_approval == True:
                if order.amount_total < self.env.user.company_id.currency_id._convert(
                            order.company_id.accountant_validation_amount, order.currency_id, order.company_id, order.date_order or fields.Date.today()):
                    order.button_approve()
                else:
                    order.write({'state': 'director'})
            order.write({'accountant_user_id': self.env.user.id, 'accountant_approve_date': fields.Date.context_today(self)})
        return True

    #Director Approve Button Funcion
    @api.multi
    def button_director_approve(self, force=False):
        for order in self:
            # Deal with Three Step validation process
            if order.company_id.po_approval == True:
                order.button_approve()
            order.write({'director_user_id': self.env.user.id, 'director_approve_date': fields.Date.context_today(self)})
        return True

    #Override Confirm Button function
    #Remove default purchase Order approval
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with Three Step validation process
            if order.company_id.po_approval == True:
                order.write({'state': 'manager'})
            else:
                order.button_approve()
        return True