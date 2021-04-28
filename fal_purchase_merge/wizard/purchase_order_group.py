# -*- encoding: utf-8 -*-
from odoo import models, api, _, fields
from odoo.exceptions import Warning


class purchase_order_group(models.TransientModel):
    _name = "purchase.order.group"
    _description = "Purchase Order Merge"

    merge_line = fields.Boolean("Merge line Quantity", default=False)

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        context = self._context or {}
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        res = super(purchase_order_group, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if context.get('active_model', '') == 'purchase.order':
            if len(context['active_ids']) < 2:
                raise Warning(_('Please select multiple orders.'))
            po = self.env['purchase.order'].browse(context['active_ids'])
            for p in po:
                if p['state'] != 'draft':
                    raise Warning(
                        _('At least one of the selected purchases is %s!') %
                        p['state'])
                if p['picking_type_id'] != po[0]['picking_type_id']:
                    raise Warning(
                        _('Cannot merge this draft PO for different Location!'))
                if p['partner_id'] != po[0]['partner_id']:
                    raise Warning(
                        _('Cannot merge this draft PO for different Partner!'))
                if p['currency_id'] != po[0]['currency_id']:
                    raise Warning(
                        _('Cannot merge this draft PO for different Currency!'))
                if p['company_id'] != po[0]['company_id']:
                    raise Warning(
                        _('Cannot merge this draft PO for different Company!'))
        return res

    @api.multi
    def merge_orders(self):
        context = self._context or {}
        """
             To merge similar type of purchase orders.

             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param ids: the ID or list of IDs
             @param context: A standard dictionary

             @return: purchase order view

        """
        order_obj = self.env['purchase.order']
        allorders = order_obj.browse(context.get('active_ids', [])).do_merge(self.merge_line)

        return {
            'domain': "[('id','in', [" + ','.join(
                map(str, allorders.keys())) + "])]",
            'name': _('Request for Quotations'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'views': [(self.env.ref(
                'purchase.purchase_order_tree').id, 'tree'
            ), (self.env.ref('purchase.purchase_order_form').id, 'form')],
            'type': 'ir.actions.act_window',
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
