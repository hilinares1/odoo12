# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools,_


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    _description = 'Stock Landed Cost'

    account_move_count = fields.Integer(string='Moves Count', compute='_get_account_moves', readonly=True)

    @api.one
    def _get_account_moves(self):
        move_obj = self.env['account.move']
        self.account_move_count = move_obj.search_count(['|',
                                                         ('ref', 'like', self.account_move_id.name),
                                                         ('id', 'in', self.account_move_id.ids)])

    @api.multi
    def action_view_account_moves(self):
        xml_id = 'account.view_move_tree'
        tree_view_id = self.env.ref(xml_id).id
        xml_id = 'account.view_move_form'
        form_view_id = self.env.ref(xml_id).id
        return {
            'name': _('Moves'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree'),
                      (form_view_id, 'form')],
            'res_model': 'account.move',
            'domain': ['|',
                       ('ref', 'like', self.account_move_id.name),
                       ('id', 'in', self.account_move_id.ids)],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def button_cancel(self):
        for stock in self:
            stock.account_move_id.button_cancel()
            #for aml in stock.account_move_id : 

            stock.account_move_id.unlink()

            for line in stock.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                    # Prorate the value at what's still in stock
                    cost_to_add = (line.move_id.remaining_qty / line.move_id.product_qty) * line.additional_landed_cost

                    new_landed_cost_value = line.move_id.landed_cost_value - line.additional_landed_cost
                    line.move_id.write({
                        'landed_cost_value': new_landed_cost_value,
                        'value': line.move_id.value - line.additional_landed_cost,
                        'remaining_value': line.move_id.remaining_value - cost_to_add,
                        'price_unit': (line.move_id.value + line.additional_landed_cost) / line.move_id.product_qty,
                    })
                    
                
            
                    line.unlink()
        return self.write({'state': 'cancel'})


    @api.multi
    def action_draft(self):
        orders = self.filtered(lambda s: s.state in ['cancel'])
        return orders.write({
            'state': 'draft',
        })
