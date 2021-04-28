# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fal_warning_text = fields.Text(string='Warning', compute='get_fal_warning_messages')

    @api.multi
    def fal_add_data_text(self, warn, data_text, data_to_insert, field_name):
        for item in data_text:
            if item.get('warning_id', False) and item.get('warning_id') == warn:
                if item.get(field_name, False):
                    if data_to_insert not in item.get(field_name):
                        item.get(field_name).append(data_to_insert)
                    return data_text
                else:
                    item[field_name] = [data_to_insert]
                    return data_text
        data_text.append({
            'warning_id': warn,
            field_name: [data_to_insert]
        })
        return data_text

    @api.model
    def get_data_text(self, mrp, data_text):
        if mrp.routing_id:
            for warn in mrp.routing_id.fal_warning_message_ids:
                mrp.fal_add_data_text(warn, data_text, mrp.routing_id, 'Routing')

        for workcentline in mrp.workorder_ids:
            if workcentline.workcenter_id:
                for warn in workcentline.workcenter_id.fal_warning_message_ids:
                    mrp.fal_add_data_text(warn, data_text, workcentline.workcenter_id, 'Workcenter')

        for move in mrp.move_finished_ids:
            for warn in move.product_id.fal_warning_message_ids:
                mrp.fal_add_data_text(warn, data_text, move.product_id, 'Product')
            for warn in move.product_id.product_tmpl_id.categ_id.fal_warning_message_ids:
                mrp.fal_add_data_text(warn, data_text, move.product_id.product_tmpl_id.categ_id, 'Product Category')

        for move in mrp.move_raw_ids:
            for warn in move.product_id.fal_cons_warning_message_ids:
                mrp.fal_add_data_text(warn, data_text, move.product_id, 'Product')
            for warn in move.product_id.product_tmpl_id.categ_id.fal_cons_warning_message_ids:
                mrp.fal_add_data_text(warn, data_text, move.product_id.product_tmpl_id.categ_id, 'Product Category')
        return data_text

    @api.depends(
        'routing_id.fal_warning_message_ids', 'product_id.fal_warning_message_ids',
        'workorder_ids.workcenter_id.fal_warning_message_ids',
        'move_finished_ids.product_id.fal_warning_message_ids',)
    def get_fal_warning_messages(self):
        for mrp in self:
            warning_text = ''
            data_text = []
            data_text = self.get_data_text(mrp, data_text)
            if mrp.fal_mo_line_ids:
                childs = self.get_fal_children(mrp.fal_mo_line_ids, [])
                for item in childs:
                    data_text = self.get_data_text(item, data_text)
            if data_text:
                warning_text = 'WARNING!!!\n'
                number = 1
                for item in data_text:
                    line_text = ''
                    for k, v in item.items():
                        if k == 'warning_id':
                            line_text = v.description + ' ' + line_text
                        else:
                            line_detail = '[' + k + ': '
                            for x in v:
                                line_detail += x.name + ', '
                            line_detail += '] '
                            line_text += line_detail
                    line_text = str(number) + '. ' + line_text + '\n'
                    warning_text += line_text
                    number += 1
            mrp.fal_warning_text = warning_text

    @api.model
    def get_fal_children(self, fal_mo_line_ids, objs):
        if fal_mo_line_ids:
            for item in fal_mo_line_ids:
                res = self.get_fal_children(item.fal_mo_line_ids, objs)
                objs.append(item)
                objs += res
        return objs
