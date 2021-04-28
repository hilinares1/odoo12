from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fal_production_order_id = fields.Many2one(
        'fal.production.order',
        string='Production Order',
        copy=False)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # in order to show prod_id in notebook
    fal_production_order_ids = fields.Many2many(
        'fal.production.order',
        compute='_compute_fal_production_order_ids',
        string='Production Order')

    # compute to show prod_id in notebook
    @api.multi
    @api.depends('order_line')
    def _compute_fal_production_order_ids(self):
        production_id = []
        for order in self:
            for order_line_id in order.order_line:
                prod_id = order_line_id.fal_production_order_id.id
                if prod_id:
                    production_id.append(prod_id)
                    if production_id:
                        order.fal_production_order_ids = [(
                            6, 0, production_id)]
