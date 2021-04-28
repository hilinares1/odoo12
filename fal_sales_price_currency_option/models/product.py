# -*- coding: utf-8 -*-
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class product_product(models.Model):
    _inherit = 'product.template'


    fal_currency_option = fields.Boolean(
        string='Sales Currency Option', default=lambda self:self.env['ir.config_parameter'].sudo().get_param('fal_config_setting.fal_sales_price_option'),
        help="Option to change behaviour of sales price currency in product .\n"
             " * Checked : Sales price will use currency of company that were logged in.\n"
             " * Unchecked : Currency of sales price taken from company field inside product. (If company field is blank currency taken from parent company")
    list_price = fields.Float(company_dependent=True)


    @api.multi
    def _compute_currency_id(self):
        res = super(product_product, self)._compute_currency_id()
        for product in self:
            if product.fal_currency_option:
                product.currency_id = product.cost_currency_id
        return res

# End of product_product()
