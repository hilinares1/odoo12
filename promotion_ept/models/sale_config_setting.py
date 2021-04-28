from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    promotion_product_id = fields.Many2one(
        'product.product',
        'Promotion Product',
        domain="[('is_promo_product', '=', True)]",context="{'default_is_promo_product':1,'default_type':'service'}",
        help='Default product used for promotion apply in sale order', config_parameter='sale.promotion_product_id')
    
    promotion_product_category_id = fields.Many2one(
        'product.category',
        'Promotion Product Category',
        help='Default product used for promotion apply in sale order', config_parameter='sale.promotion_product_category_id')


    group_promotion_product = fields.Boolean("Create Promotion Product", implied_group='promotion_ept.group_promotion_product', group="promotion_ept.group_promotion_manager")
    
    group_promo_product_show = fields.Boolean("Show Promotion Product", implied_group='promotion_ept.group_promotion_product_show', group="promotion_ept.group_promotion_manager")

    @api.model
    def get_values(self):
        res = super(SaleConfiguration, self).get_values()
        group_promotion_product = self.env['ir.config_parameter'].sudo().get_param('sale.group_promotion_product')
        group_promotion_product_show = self.env['ir.config_parameter'].sudo().get_param('sale.group_promo_product_show')
        return res

    @api.multi
    def set_values(self):
        super(SaleConfiguration, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
             'sale.promotion_product_id', self.promotion_product_id.id)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale.promotion_product_category_id', self.promotion_product_category_id.id)
        print(self.group_promotion_product, self.group_promo_product_show)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale.group_promotion_product', self.group_promotion_product)
        self.env['ir.config_parameter'].sudo().set_param(
            'sale.group_promo_product_show', self.group_promo_product_show)
    
    @api.constrains('promotion_product_id','promotion_product_category_id')
    def _check_something(self):
        for record in self:
            if record.promotion_product_id.categ_id!=record.promotion_product_category_id:
                raise ValidationError("Promotion Product's category sould be match with promotion product category")