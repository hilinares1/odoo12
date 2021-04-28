# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    fal_product_categ_id = fields.Many2one(
        'product.category'
    )
    # Can't make this related only to product template
    product_uom = fields.Many2one(
        compute='_compute_product_uom', related=False)

    @api.one
    def _compute_product_uom(self):
        if self.product_tmpl_id:
            self.product_uom = self.product_tmpl_id.uom_po_id
        elif self.fal_product_categ_id:
            self.product_uom = self.fal_product_categ_id.fal_uom_po_id


class ProductCategory(models.Model):
    _inherit = 'product.category'

    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order='id').id

    fal_seller_ids = fields.One2many(
        'product.supplierinfo',
        'fal_product_categ_id',
        string='Vendors'
    )
    fal_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default unit of measure used for all stock operations.")
    fal_uom_name = fields.Char(string='Unit of Measure Name', related='fal_uom_id.name', readonly=True)
    fal_uom_po_id = fields.Many2one(
        'uom.uom', 'Purchase Unit of Measure',
        default=_get_default_uom_id, required=True,
        help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.")

    @api.onchange('fal_uom_id')
    def _onchange_fal_uom_id(self):
        if self.fal_uom_id:
            self.fal_uom_po_id = self.fal_uom_id.id

    @api.constrains('fal_uom_id', 'fal_uom_po_id')
    def _check_uom(self):
        if any(category.fal_uom_id and category.fal_uom_po_id and category.fal_uom_id.category_id != category.fal_uom_po_id.category_id for category in self):
            raise ValidationError(_('The default Unit of Measure and the purchase Unit of Measure must be in the same category.'))
        return True


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.one
    def _compute_product_code(self):
        if self.seller_ids:
            super(ProductProduct, self)._compute_product_code()
        else:
            for supplier_info in self.categ_id.fal_seller_ids:
                if supplier_info.name.id == self._context.get('partner_id'):
                    self.code = supplier_info.product_code or self.default_code
                    break
            else:
                self.code = self.default_code

    @api.one
    def _compute_partner_ref(self):
        if self.seller_ids:
            super(ProductProduct, self)._compute_partner_ref()
        else:
            for supplier_info in self.categ_id.fal_seller_ids:
                if supplier_info.name.id == self._context.get('partner_id'):
                    product_name = supplier_info.fal_product_categ_id.name or self.default_code or self.name
                    self.partner_ref = '%s%s' % (self.code and '[%s] ' % self.code or '', product_name)
                    break
            else:
                self.partner_ref = self.name_get()[0][1]

    def _prepare_sellers(self, params):
        if self.seller_ids:
            return super(ProductProduct, self)._prepare_sellers(params)
        else:
            return self.categ_id.fal_seller_ids
