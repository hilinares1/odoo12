# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"


    company_id = fields.Many2one('res.company', required=False)
