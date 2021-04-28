# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _order_revised_count(self):
        fal_order_revised_count = self.env['sale.order'].search(
            [('fal_parent_so_id', '=', self.id), ('active', '=', False)])
        self.fal_order_revised_count = len(fal_order_revised_count)

    name = fields.Char(string='Order Reference', required=True, copy=False,
                       readonly=True, index=True, default='New')
    fal_parent_so_id = fields.Many2one(
        'sale.order', 'Parent SaleOrder', copy=False)
    fal_order_revised_count = fields.Integer(
        '# of Orders Revised', compute='_order_revised_count', copy=False)
    fal_so_number = fields.Integer('SO Number', copy=False, default=1)
    is_revised_so = fields.Boolean(string="Is Revised Order", default=False)

    @api.multi
    def so_revision_quote(self):
        for cur_rec in self:
            if not cur_rec.origin:
                origin_name = cur_rec.name
                cur_rec.origin = cur_rec.name
            else:
                origin_name = cur_rec.origin

            vals = {
                'name': origin_name + ' v' + str(cur_rec.fal_so_number),
                'state': 'sent',
                'fal_parent_so_id': cur_rec.id,
                'is_revised_so': True,
                'active': False
            }
            cur_rec.copy(default=vals)
            cur_rec.state = 'draft'
            cur_rec.fal_so_number += 1

    # @api.multi
    # def _action_confirm(self):
    #     res = super(SaleOrder, self)._action_confirm()
    #     child_id = self.search(
    #         [('fal_parent_so_id', '=', self.id)], order="create_date desc",
    #         limit=1)
    #     if child_id:
    #         child_id.name = self.name
    #     return res
