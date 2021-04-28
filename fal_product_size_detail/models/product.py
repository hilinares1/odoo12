from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def fal_get_domain_length(self):
        return [(
            'category_id', '=',
            self.env.ref('uom.uom_categ_length').id
        )]

    # Add the fields Length / Width / Height
    fal_length = fields.Float('Length')
    fal_length_uom_id = fields.Many2one(
        'uom.uom', string='Length UoM',
        domain=fal_get_domain_length,
    )
    fal_width = fields.Float('Width')
    fal_width_uom_id = fields.Many2one(
        'uom.uom', string='Width UoM',
        domain=fal_get_domain_length,
    )
    fal_height = fields.Float('Height')
    fal_height_uom_id = fields.Many2one(
        'uom.uom', string='Height UoM',
        domain=fal_get_domain_length,
    )
    volume = fields.Float(
        'Volume', compute='fal_get_volume',
        digits=dp.get_precision('Stock Volume')
    )

    @api.depends(
        'fal_length', 'fal_length_uom_id',
        'fal_width', 'fal_width_uom_id',
        'fal_height', 'fal_height_uom_id'
    )
    def fal_get_volume(self):
        for prod in self:
            if not prod.fal_length_uom_id or\
                not prod.fal_width_uom_id or \
                    not prod.fal_height_uom_id:
                prod.volume = 0.0
            else:
                fal_length = prod.fal_length_uom_id._compute_quantity(
                    prod.fal_length,
                    self.env.ref('uom.product_uom_meter')
                )
                fal_width = prod.fal_width_uom_id._compute_quantity(
                    prod.fal_width,
                    self.env.ref('uom.product_uom_meter')
                )
                fal_height = prod.fal_height_uom_id._compute_quantity(
                    prod.fal_height,
                    self.env.ref('uom.product_uom_meter')
                )
                prod.volume = fal_length * fal_width * fal_height


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def fal_get_domain_length(self):
        return [(
            'category_id', '=',
            self.env.ref('uom.uom_categ_length').id
        )]

    # Add the fields Length / Width / Height
    fal_length = fields.Float(
        'Length',
        compute='_compute_fal_length',
        inverse='_set_fal_length',
        store=True
    )
    fal_length_uom_id = fields.Many2one(
        'uom.uom', string='Length UoM',
        compute='_compute_fal_length_uom_id',
        inverse='_set_fal_length_uom_id',
        store=True,
        domain=fal_get_domain_length,
    )
    fal_width = fields.Float(
        'Width',
        compute='_compute_fal_width',
        inverse='_set_fal_width',
        store=True
    )
    fal_width_uom_id = fields.Many2one(
        'uom.uom', string='Width UoM',
        compute='_compute_fal_width_uom_id',
        inverse='_set_fal_width_uom_id',
        store=True,
        domain=fal_get_domain_length,
    )
    fal_height = fields.Float(
        'Height',
        compute='_compute_fal_height',
        inverse='_set_fal_height',
        store=True
    )
    fal_height_uom_id = fields.Many2one(
        'uom.uom', string='Height UoM',
        compute='_compute_fal_height_uom_id',
        inverse='_set_fal_height_uom_id',
        store=True,
        domain=fal_get_domain_length,
    )
    volume = fields.Float(inverse='', digits=dp.get_precision('Stock Volume'))

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_length',
    )
    def _compute_fal_length(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_length = template.product_variant_ids.fal_length
        for template in (self - unique_variants):
            template.fal_length = 0.0

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_width',
    )
    def _compute_fal_width(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_width = template.product_variant_ids.fal_width
        for template in (self - unique_variants):
            template.fal_width = 0.0

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_height',
    )
    def _compute_fal_height(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_height = template.product_variant_ids.fal_height
        for template in (self - unique_variants):
            template.fal_height = 0.0

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_length_uom_id',
    )
    def _compute_fal_length_uom_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_length_uom_id = template.product_variant_ids.\
                fal_length_uom_id
        for template in (self - unique_variants):
            template.fal_length_uom_id = self.env.ref(
                'uom.product_uom_meter'
            ).id

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_width_uom_id',
    )
    def _compute_fal_width_uom_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_width_uom_id = template.product_variant_ids.\
                fal_width_uom_id
        for template in (self - unique_variants):
            template.fal_width_uom_id = self.env.ref(
                'uom.product_uom_meter'
            ).id

    @api.depends(
        'product_variant_ids',
        'product_variant_ids.fal_height_uom_id',
    )
    def _compute_fal_height_uom_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.fal_height_uom_id = template.product_variant_ids.\
                fal_height_uom_id
        for template in (self - unique_variants):
            template.fal_height_uom_id = self.env.ref(
                'uom.product_uom_meter'
            ).id

    @api.model
    def _set_fal_length(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_length = self.fal_length

    @api.model
    def _set_fal_width(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_width = self.fal_width

    @api.model
    def _set_fal_height(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_height = self.fal_height

    @api.model
    def _set_fal_length_uom_id(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_length_uom_id = self.fal_length_uom_id

    @api.model
    def _set_fal_width_uom_id(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_width_uom_id = self.fal_width_uom_id

    @api.model
    def _set_fal_height_uom_id(self):
        self.ensure_one()
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.fal_height_uom_id = self.fal_height_uom_id

    @api.depends(
        'fal_length',
        'fal_width',
        'fal_height',
        'fal_length_uom_id',
        'fal_width_uom_id',
        'fal_height_uom_id',
    )
    def _compute_volume(self):
        for prod in self:
            if not prod.fal_length_uom_id or\
                not prod.fal_width_uom_id or \
                    not prod.fal_height_uom_id:
                prod.volume = 0.0
            else:
                fal_length = prod.fal_length_uom_id._compute_quantity(
                    prod.fal_length,
                    self.env.ref('uom.product_uom_meter')
                )
                fal_width = prod.fal_width_uom_id._compute_quantity(
                    prod.fal_width,
                    self.env.ref('uom.product_uom_meter')
                )
                fal_height = prod.fal_height_uom_id._compute_quantity(
                    prod.fal_height,
                    self.env.ref('uom.product_uom_meter')
                )
                prod.volume = fal_length * fal_width * fal_height
