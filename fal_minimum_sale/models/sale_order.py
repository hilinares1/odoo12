from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_below_minimum = fields.Boolean("Below Minimum Price", compute="_is_below_minimum")
    is_above_maximum = fields.Boolean("Above Maximum Price", compute="_is_above_maximum")

    def check_price_above_maximum(self):
        if not self.product_id or not self.product_uom_qty or not self.price_subtotal or not self.order_id.pricelist_id:
            return False
        else:
            # Get the correct pricelist item
            PricelistItem = self.env['product.pricelist.item']
            precision = self.env['decimal.precision'].precision_get('Product Price')
            final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            pricelist_item = PricelistItem.browse(rule_id)

            # Max product price based on user group
            max_product_price = final_price + (pricelist_item.fal_salesman_max_increase * final_price / 100)
            # Count the unit price on this sale order line
            product_unit_price = self.price_subtotal / self.product_uom_qty
            if float_compare(max_product_price, product_unit_price, precision_digits=precision) == -1:
                return True
        return False

    @api.multi
    def _is_above_maximum(self):
        for order_line in self:
            order_line.is_above_maximum = order_line.check_price_above_maximum()

    @api.onchange('price_subtotal', 'product_uom_qty')
    def _onchange_check_maximum_price(self):
        if self.check_price_above_maximum() and not self.user_has_groups('sales_team.group_sale_manager'):
            # Get the correct pricelist item, then check the maximum sale price on it
            PricelistItem = self.env['product.pricelist.item']
            final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            pricelist_item = PricelistItem.browse(rule_id)

            # Max product price based on user group
            max_product_price = final_price + (pricelist_item.fal_salesman_max_increase * final_price / 100)
            # Count the unit price on this sale order line
            product_unit_price = self.price_subtotal / self.product_uom_qty

            message = _("Unit Price of Product ") + self.product_id.display_name + " (" + str(product_unit_price) + _(") Is Above Maximum Price (") + str(max_product_price) + ")"
            warning_mess = {
                'title': _('Above Maximum Price!'),
                'message': message
            }
            return {'warning': warning_mess}
        else:
            return {}

    def check_price_below_minimum(self):
        if not self.product_id or not self.product_uom_qty or not self.price_subtotal or not self.order_id.pricelist_id:
            return False
        else:
            # Get the correct pricelist item
            PricelistItem = self.env['product.pricelist.item']
            precision = self.env['decimal.precision'].precision_get('Product Price')
            final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            pricelist_item = PricelistItem.browse(rule_id)

            # Min product price based on user group
            min_product_price = final_price - (pricelist_item.fal_salesman_max_reduce * final_price / 100)
            # Count the unit price on this sale order line
            product_unit_price = self.price_subtotal / self.product_uom_qty
            if float_compare(min_product_price, product_unit_price, precision_digits=precision) == 1:
                return True
        return False

    @api.multi
    def _is_below_minimum(self):
        for order_line in self:
            order_line.is_below_minimum = order_line.check_price_below_minimum()

    @api.onchange('price_subtotal', 'product_uom_qty')
    def _onchange_check_minimum_price(self):
        if self.check_price_below_minimum() and not self.user_has_groups('sales_team.group_sale_manager'):
            # Get the correct pricelist item, then check the minimum sale price on it
            PricelistItem = self.env['product.pricelist.item']
            final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
            pricelist_item = PricelistItem.browse(rule_id)

            # Min product price based on user group
            min_product_price = final_price - (pricelist_item.fal_salesman_max_reduce * final_price / 100)
            # Count the unit price on this sale order line
            product_unit_price = self.price_subtotal / self.product_uom_qty

            message = _("Unit Price of Product ") + self.product_id.display_name + " (" + str(product_unit_price) + _(") Is Below Minimum Price (") + str(min_product_price) + ")"
            warning_mess = {
                'title': _('Below Minimum Price!'),
                'message' : message
            }
            return {'warning': warning_mess}
        else:
            return {}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_proposal(self):
        if super(SaleOrder, self)._check_proposal():
            return True
        else:
            order_line_below_minimum = False
            order_line_above_maximum = False

            for order_line in self.order_line:
                if order_line.is_below_minimum:
                    order_line_below_minimum = True
                if order_line.is_above_maximum:
                    order_line_above_maximum = True
            if order_line_below_minimum:
                return True
            elif order_line_above_maximum:
                return True
            else:
                return False
