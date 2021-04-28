from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'sale.order'

    fal_of_number = fields.Char('PO Number', copy=False)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        res = super(StockRule, self)._run_manufacture(product_id, product_qty, product_uom, location_id, name, origin, values)
        stock_move = values.get('move_dest_ids')
        for move in stock_move:
            purchase = move.sale_line_id.order_id.auto_purchase_order_id
            if purchase.fal_of_number:
                sales = self.env['sale.order'].search([('name', 'in', purchase.origin.split(", "))])
                for sale in sales:
                    sale.write({'fal_of_number': purchase.fal_of_number})
        return res
