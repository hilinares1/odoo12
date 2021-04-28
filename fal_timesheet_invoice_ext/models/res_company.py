# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = "res.company"
 
    fal_use_late_payment_statement = fields.Text('Late payment statement', translate=True)