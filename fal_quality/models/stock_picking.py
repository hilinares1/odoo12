from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.backorder_id:
            stock_picking = self.search([('id', '=', res.backorder_id.id)])
            if stock_picking:
                quality_check_obj = self.env['quality.check'].sudo()
                quality_check = quality_check_obj.search([('picking_id', '=', stock_picking.id)])
                if quality_check:
                    quality_length = len(quality_check)
                    value = int(quality_length / 2)
                    for data in range(value, quality_length):
                        quality_check[value].write({'picking_id': res.id, })
                        value += 1
        return res

    @api.multi
    def action_done(self):
        # Map the quality check by product, if all of it has at least 1 pass, then we consider it as pass
        quality_check_pass = self.mapped('check_ids').filtered(lambda x: x.quality_state == 'pass').mapped('product_id')
        all_quality_check = self.mapped('check_ids').mapped('product_id')
        if quality_check_pass < all_quality_check:
            raise UserError(_('Cannot validate, there is failed / not checked product quality'))
        return super(StockPicking, self).action_done()
