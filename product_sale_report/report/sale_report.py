# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    latitude = fields.Float(related='partner_id.partner_latitude')
    longitude = fields.Float(related='partner_id.partner_longitude')
