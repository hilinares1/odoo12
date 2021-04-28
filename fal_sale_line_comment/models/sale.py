# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fal_comment_line_ids = fields.One2many(
        'fal.comment.line', 'sale_line_id', string="Comments")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        for item in self:
            if item.product_id:
                data = []
                comment_template = item._prepare_comment_template()
                if comment_template:
                    for comment in comment_template:
                        line = {
                            'fal_comment_template_id': comment.id,
                            'value': comment.name,
                        }
                        data.append((0, 0, line))
                        item.fal_comment_line_ids = data
                        item.name += ' ' + comment.name
                else:
                    item.fal_comment_line_ids = data
        return res

    @api.multi
    def _prepare_comment_template(self):
        for item in self:
            return self.env['fal.comment.template'].search([
                '&', '|',
                ('product_ids', '=', item.product_id.id),
                ('product_ids', '=', False),
                '|',
                ('partner_ids', '=', item.order_id.partner_id.id),
                ('partner_ids', '=', False),
            ])
