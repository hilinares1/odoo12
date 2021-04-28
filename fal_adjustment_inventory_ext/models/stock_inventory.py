from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Inventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['mail.thread', 'stock.inventory']

    # need confimation about lock, row, case to active this function
    # fal_shelf = fields.Char(
    #     string='Shelf',
    #     readonly=True,
    #     states={'draft': [('readonly', False)]},
    #     help='You can do more than 1 shelf, example: shelf1;shelf2;shelf3')

    @api.model
    def _selection_filter(self):
        res = super(Inventory, self)._selection_filter()
        res.append(('by categories', _('By Product Categories')))
        # res.append(('by shelf', _('By Shelf')))
        return res

    @api.onchange('filter')
    def _onchange_filter(self):
        res = super(Inventory, self)._onchange_filter()
        if self.filter != 'by categories':
            self.category_id = False
        # if self.filter != 'by shelf':
        #     self.fal_shelf = False
        return res

    def _get_inventory_lines_values(self):
        if self.filter == 'by categories':
        # if self.filter in ('by categories', 'by shelf') :
            locations = self.env['stock.location'].search([('id', 'child_of', [self.location_id.id])])
            domain = ' location_id in %s AND quantity != 0'
            args = (tuple(locations.ids),)

            vals = []
            Product = self.env['product.product']
            # Empty recordset of products available in stock_quants
            quant_products = self.env['product.product']
            # Empty recordset of products to filter
            products_to_filter = self.env['product.product']
            if self.category_id:
                categ_products = Product.search([('categ_id', 'child_of', self.category_id.id)])
                domain += ' AND product_id = ANY (%s)'
                args += (categ_products.ids,)
                products_to_filter |= categ_products
            # if self.fal_shelf:
            #     shelfs = self.fal_shelf.replace(' ', '').split(';')
            #     products = Product.search([('loc_rack', 'in', shelfs)])
            #     if not products:
            #         raise UserError(_("Product doesnt exist in shelfs!"))
            #     domain += ' AND product_id = ANY (%s)'
            #     args += (products.ids,)
            #     products_to_filter |= products

            self.env.cr.execute("""SELECT product_id, sum(quantity) as product_qty, location_id, lot_id as prod_lot_id, package_id, owner_id as partner_id
                FROM stock_quant
                WHERE %s
                GROUP BY product_id, location_id, lot_id, package_id, partner_id """ % domain, args)

            for product_data in self.env.cr.dictfetchall():
                # replace the None the dictionary by False, because falsy values are tested later on
                for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                    product_data[void_field] = False
                product_data['theoretical_qty'] = product_data['product_qty']
                if product_data['product_id']:
                    product_data['product_uom_id'] = Product.browse(product_data['product_id']).uom_id.id
                    quant_products |= Product.browse(product_data['product_id'])
                vals.append(product_data)
            if self.exhausted:
                exhausted_vals = self._get_exhausted_inventory_line(products_to_filter, quant_products)
                vals.extend(exhausted_vals)
            return vals
        else:
            return super(Inventory, self)._get_inventory_lines_values()


class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    fal_explanation = fields.Text(string='Explanation')
    fal_is_adjustment = fields.Boolean(compute='_compute_fal_is_adjustment', string='Is Adjustment')

    @api.multi
    @api.depends('theoretical_qty', 'product_qty')
    def _compute_fal_is_adjustment(self):
        for inventory_line in self:
            inventory_line.fal_is_adjustment = inventory_line.theoretical_qty != inventory_line.product_qty
