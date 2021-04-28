from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    fal_lead_ids = fields.One2many(
        'fal.crm.lead.line',
        'lead_id',
        string='Products'
    )

    fal_wishlist_number = fields.Char(
        'Wishlist Number', copy=False, default='New'
    )

    @api.model
    def create(self, vals):
        if vals.get('fal_wishlist_number', 'New') == 'New':
            vals['fal_wishlist_number'] = self.env['ir.sequence']\
                .next_by_code('wish.number') or 'New'
        result = super(CrmLead, self).create(vals)
        return result

    # Ask Wizard
    # @api.multi
    # def open_selection_wizard(self):
    #     self.ensure_one()
    #     ctx = dict(self._context)
    #     ctx['default_partner_id'] = self.partner_id and self.partner_id.id or\
    #         False
    #     form_view_ref = self.env.ref(
    #         'fal_crm_wishlist.fal_lead_prod_select_form_view',
    #         False
    #     )
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Select Product'),
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'res_model': 'fal.prod.select.wizard',
    #         'nodestroy': True,
    #         'target': 'new',
    #         'views': [
    #             (form_view_ref and form_view_ref.id, 'form')
    #         ],
    #         'context': ctx,
    #     }


class FalCrmLeadLine(models.Model):
    _name = 'fal.crm.lead.line'

    @api.model
    def fal_get_domain_length(self):
        return [(
            'category_id', '=',
            self.env.ref('product.uom_categ_length').id
        )]

    name = fields.Char(
        string='Description'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product'
    )
    fal_length = fields.Float(
        'Length',
        related='product_id.fal_length'
    )
    fal_length_uom_id = fields.Many2one(
        'uom.uom', string='Length UoM',
        related='product_id.fal_length_uom_id'
    )
    fal_width = fields.Float(
        'Width',
        related='product_id.fal_width'
    )
    fal_width_uom_id = fields.Many2one(
        'uom.uom', string='Width UoM',
        related='product_id.fal_width_uom_id'
    )
    fal_height = fields.Float(
        'Height',
        related='product_id.fal_height'
    )
    fal_height_uom_id = fields.Many2one(
        'uom.uom', string='Height UoM',
        related='product_id.fal_height_uom_id'
    )
    image = fields.Binary(
        string="Image",
        related='product_id.image_medium'
    )
    # Field from fal_product_old_ref module
    # fal_old_ref = fields.Char(
    #     string='Old Ref.',
    #     related='product_id.fal_old_ref'
    # )
    lead_id = fields.Many2one(
        'crm.lead',
        string='Lead/Opportunity'
    )
    wishlist_price_ids = fields.One2many(
        'fal.wishlist.pricelist.line',
        'lead_line_id',
        string='Pricelist Details',
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency'
    )
    packaging_attr_id = fields.Many2one(
        'product.attribute.value',
        string='Packaging',
        compute='get_attributes'
    )
    color_attr_id = fields.Many2one(
        'product.attribute.value',
        string='Color',
        compute='get_attributes'
    )
    material_attr_id = fields.Many2one(
        'product.attribute.value',
        string='Material',
        compute='get_attributes'
    )
    remark_attr_id = fields.Text(
        string='Remark'
    )

    @api.depends(
        'product_id', 'product_id.attribute_value_ids',
        'product_id.attribute_value_ids.attribute_id',
        'product_id.attribute_value_ids.attribute_id.name')
    def get_attributes(self):
        for line in self:
            for item in line.product_id.attribute_value_ids:
                name = item.attribute_id.name.strip().lower() or ''
                if name == 'packaging' or\
                        item.attribute_id.fal_attr_usage == 'packaging':
                    line.packaging_attr_id = item
                elif name == 'color' or\
                        item.attribute_id.fal_attr_usage == 'color':
                    line.color_attr_id = item
                elif name == 'material' or\
                        item.attribute_id.fal_attr_usage == 'material':
                    line.material_attr_id = item


class FalWishlistPricelistLine(models.Model):
    _name = 'fal.wishlist.pricelist.line'

    min_qty = fields.Float(
        string='Min. Quantity'
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='UoM'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency'
    )
    price = fields.Monetary(
        string='Price',
    )
    lead_line_id = fields.Many2one(
        'fal.crm.lead.line',
        string='Lead Line'
    )
