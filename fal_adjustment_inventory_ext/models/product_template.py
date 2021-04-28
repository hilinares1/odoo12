from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    loc_rack = fields.Char(string='Rack', size=16)
    loc_row = fields.Char(string='Row', size=16)
    loc_case = fields.Char(string='Case', size=16)
