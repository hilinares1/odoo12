# -*- coding: utf-8 -*-
from odoo import fields, models


class FalCommentTemplate(models.Model):
    _inherit = 'fal.comment.template'

    partner_ids = fields.Many2many('res.partner', string='Customer', domain="[('customer', '=', True)]")
    product_ids = fields.Many2many('product.product', string='Product')


class FalCommentLine(models.Model):
    _inherit = 'fal.comment.line'

    sale_line_id = fields.Many2one('sale.order.line')
