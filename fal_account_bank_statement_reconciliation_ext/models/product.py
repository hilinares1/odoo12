# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class product_category(models.Model):
    _name = 'product.category'
    _inherit = 'product.category'

    property_account_general_id = fields.Many2one(
        'account.account',
        string="Statement Account",
        help="This account will be used for statement\
        instead of the default one to value for the current product."
    )

# end of product_category()


class product_template(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    property_account_general_id = fields.Many2one(
        'account.account',
        string="Statement Account",
        help="This account will be used for statement\
        instead of the default one to value for the current product."
    )

# end of product_product()
