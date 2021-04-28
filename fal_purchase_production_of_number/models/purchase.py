from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fal_of_number = fields.Char('PO Number', copy=False)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        res = super(StockRule, self)._run_manufacture(product_id, product_qty, product_uom, location_id, name, origin, values)
        stock_move = values.get('move_dest_ids')
        for move in stock_move:
            fal_of_number = ""
            fal_prod_order = False
            if move.sale_line_id.id:
                fal_prod_order = self.env['fal.production.order'].search([('fal_sale_order_line_id', '=', move.sale_line_id.id)])
            purchase = move.sale_line_id.order_id.auto_purchase_order_id
            if purchase.fal_of_number:
                fal_of_number = move.sale_line_id.order_id.auto_purchase_order_id.fal_of_number + ', '
            if fal_prod_order:
                fal_of_number += fal_prod_order.name
            purchase.write({'fal_of_number': fal_of_number})
        return res
