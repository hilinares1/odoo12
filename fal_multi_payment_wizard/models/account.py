# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountPayment(models.Model):
    _inherit = "account.payment"

    fal_multi_payment_number = fields.Char(
        'Preparation Payment Number', size=64)


class Invoice(models.Model):
    _inherit = 'account.invoice'

    fal_multi_payment_number = fields.Char(
        'Preparation Payment Number', size=64)
