# -*- encoding: utf-8 -*-
from odoo import models, api, _
from odoo.osv.orm import browse_record_list, browse_record, browse_null


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def do_merge(self, merge_line=False):

        purchase_obj = self.env['purchase.order']

        def make_key(br, fields):
            list_key = []
            for field in fields:
                field_val = getattr(br, field)
                if field in ('product_id', 'account_analytic_id'):
                    if not field_val:
                        field_val = False
                if isinstance(field_val, browse_record):
                    field_val = field_val.id
                elif isinstance(field_val, browse_null):
                    field_val = False
                elif isinstance(field_val, browse_record_list):
                    field_val = ((6, 0, tuple([v.id for v in field_val])),)
                list_key.append((field, field_val))
            list_key.sort()
            return tuple(list_key)

        def merge_similar_line(order):
            orderlines_merged = []
            for order_line in order.order_line:
                # Do not compare orderline that has been merged
                if order_line not in orderlines_merged:
                    for order_line_compare in order.order_line.filtered(lambda r: r.id != order_line.id):
                        # List of fields that need to be same in order to merge the order line
                        if order_line.account_analytic_id == order_line_compare.account_analytic_id and\
                            order_line.analytic_tag_ids == order_line_compare.analytic_tag_ids and\
                            order_line.company_id == order_line_compare.company_id and\
                            order_line.currency_id == order_line_compare.currency_id and\
                            order_line.taxes_id == order_line_compare.taxes_id and\
                            order_line.price_unit == order_line_compare.price_unit and\
                            order_line.product_id == order_line_compare.product_id and\
                            order_line.product_uom == order_line_compare.product_uom:
                            order_line.product_qty += order_line_compare.product_qty
                            orderlines_merged.append(order_line_compare)
            # Remove all orderline that has been merged
            for orderline_merged in orderlines_merged:
                orderline_merged.unlink()


        context = self._context or {}

        # Compute what the new orders should contain
        new_orders = {}

        order_lines_to_move = {}
        for porder in [order for order in self.with_context(
                context) if order.state == 'draft']:
            order_key = make_key(porder, ['partner_id'])
            new_order = new_orders.setdefault(order_key, ({}, []))
            new_order[1].append(porder.id)
            order_infos = new_order[0]
            order_lines_to_move.setdefault(order_key, [])

            if not order_infos:
                order_infos.update({
                    'origin': porder.origin,
                    'date_order': porder.date_order,
                    'partner_id': porder.partner_id.id,
                    'dest_address_id': porder.dest_address_id.id,
                    'picking_type_id': porder.picking_type_id.id,
                    'currency_id': porder.currency_id.id,
                    'state': 'draft',
                    'order_line': {},
                    'notes': '%s' % (porder.notes or '',),
                })
            else:
                if porder.date_order < order_infos['date_order']:
                    order_infos['date_order'] = porder.date_order
                if porder.notes:
                    order_infos['notes'] = (
                        order_infos['notes'] or ''
                    ) + ('\n%s' % (porder.notes,))
                if porder.origin:
                    order_infos['origin'] = (
                        order_infos['origin'] or '') + ' ' + porder.origin

            order_lines_to_move[order_key] += [
                order_line.id for order_line in porder.order_line if order_line.state != 'cancel']

        allorders = []
        orders_info = {}
        for order_key, (order_data, old_ids) in new_orders.items():
            # skip merges with only one order
            if len(old_ids) < 2:
                allorders += (old_ids or [])
                continue

            # cleanup order line data
            for key, value in order_data['order_line'].items():
                del value['uom_factor']
                value.update(dict(key))
            order_data['order_line'] = [(6, 0, [self.env['purchase.order.line'].browse(order_line_to_move).copy().id for order_line_to_move in order_lines_to_move[order_key]])]

            # create the new order
            neworder_id = self.create(order_data)
            neworder_id.with_context(
                mail_create_nolog=True).message_post(body=_("RFQ created, combined from %s") % [order.name for order in self.with_context(
                context) if order.state == 'draft'])
            # Try to merge similar orderline
            if merge_line:
                merge_similar_line(neworder_id)
            orders_info.update({neworder_id.id: old_ids})
            allorders.append(neworder_id)

            # make triggers pointing to the old orders point to the new order
            for old_id in purchase_obj.browse(old_ids):
                old_id.write({'state': 'cancel'})
        return orders_info
