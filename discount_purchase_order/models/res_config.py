# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_order_global_discount_po = fields.Boolean("A global discount on purchase order",
        implied_group='discount_purchase_order.group_order_global_discount_po',
        help="""Allows to give a global discount on purchase order. """)
    global_discount_tax_po = fields.Selection([
        ('untax', 'Untaxed amount'),
        ('taxed', 'Tax added amount'),
        ], "Global Discount Calculation",
        help="Global disount calculation will be ( \
            'untax' : Global discount will be applied before applying tax, \
            'taxed' : Global disount will be applied after applying tax)")
    group_discount_purchase_line = fields.Boolean("Apply discount on purchase order line",
        implied_group='discount_purchase_order.group_discount_purchase_line',
        help="""Allows to give discount on purchase order line. """)

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        IrConfigPrmtr.set_param(
            "purchase.global_discount_tax_po", self.global_discount_tax_po
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfigPrmtr = self.env['ir.config_parameter'].sudo()
        globalDiscountTax = IrConfigPrmtr.get_param('purchase.global_discount_tax_po')
        res.update({
            'global_discount_tax_po' : globalDiscountTax,
        })
        return res
