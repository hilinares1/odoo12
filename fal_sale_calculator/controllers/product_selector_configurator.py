from odoo import http
from odoo.http import request
from odoo.addons.fal_product_attribute.controllers.product_selector_configurator import ProductSelectorController


class ProductSelectorCalculatorController(ProductSelectorController):
    @http.route(['/product_selector/configure'], type='json', auth="user", methods=['POST'])
    def configure(self, model, variants, many2one=False, **kw):
        # values = super(ProductSelectorCalculatorController, self).configure(variants, many2one, **kw)

        ps = request.env['product.selector'].create({
            'product_id': 0,
        })

        pslines = []
        if variants:
            for variant in variants:
                psline = request.env['product.selector.line'].create({
                    'atribute_id': variant['attribute_id'],
                    'value_id': variant['value_id'],
                    'custom_value': variant['custom_value']
                })
                pslines.append(psline.id)

        ps.product_selector_line_ids = [(6, 0, pslines)]
        ps.with_context(model=model).onchange_product_selector_line_ids()
        if ps.product_selector_line_ids:
            for product_selector_line in ps.product_selector_line_ids:
                product_selector_line.onchange_custom_value(product_selector_line.custom_value)
                domain = product_selector_line.fal_available_value_ids_change()['domain']
        else:
            domain = ps.product_selector_line_ids.fal_available_value_ids_change()['domain']

        attributes = request.env['product.attribute'].search(domain['atribute_id'])
        values = request.env['product.attribute.value'].search(domain['value_id'])

        for attribute in attributes:
            for value in attribute.value_ids:
                if value not in values:
                    filtered_values = attribute.value_ids.filtered(lambda r: r.id not in [value.id])
                    attribute.value_ids = filtered_values

        if many2one:
            return request.env['ir.ui.view'].render_template("fal_product_attribute.product_selector_configure_many2one", {
                'attributes': attributes,
                'product_ids': ps.product_ids,
                'added_price': ps.added_price,
            })
        return request.env['ir.ui.view'].render_template("fal_product_attribute.product_selector_configure", {
            'attributes': attributes,
            'product_ids': ps.product_ids,
            'added_price': ps.added_price,
        })
