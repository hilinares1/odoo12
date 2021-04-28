# -*- coding: utf-8 -*-

from odoo import fields, models


class product_product(models.Model):
    _inherit = 'product.product'

    fal_project_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        company_dependent=True,
    )

    customer_code = fields.Char(
        string='Customer Code',
        size=128
    )

    customer_ref_number = fields.Char(
        string='Customer Reference Number',
        size=128
    )
