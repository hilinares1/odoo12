# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class Company(models.Model):
    _inherit = 'res.company'

    po_approval = fields.Boolean("PO Three Step Approval")
    manager_validation_amount = fields.Monetary(string='Manager Validation Amount', default=100)
    accountant_validation_amount = fields.Monetary(string='Accountant Validation Amount', default=1000)
