# -*- coding: utf-8 -*-
##############################################################################
#
#    Expert Co. Ltd.
#    Copyright (C) 2018 (<http://www.exp-sa.com/>).
#
##############################################################################

from odoo import models, api
from odoo.http import request
from itertools import groupby
import time


class hierarchical_chart_model(models.Model):
    _name = 'hierarchical_chart_model'

    @api.model
    def hierarchical_chart_details(self, model, res_id=False):
        """
        get the list of dicts in sorted oreder to fit in hierarchy view
        """
        if res_id:
            keys, data = self.env[model].search(
                [('id', '=', res_id)]).hierarchical_chart_details()
        else:
            keys, data = self.env[model].hierarchical_chart_details()

        model_id = self.env['ir.model'].search([('model', '=', model)])
        fields = self.env['ir.model.fields'].search(
            [('model_id', 'in', model_id.ids)])
        fields = fields.read(['name', 'field_description', 'ttype'])

        fields_names = {x['name']: x['field_description'] for x in fields}

        fields_types = {x['name']: x['ttype'] for x in fields}

        all_data = []
        groupby_dicts = {}
        for rec in data:
            key = rec['parent_id'] and rec['parent_id'][0] or False
            value = rec

            if key:
                groupby_dicts[key] = groupby_dicts.get(key, [])
                groupby_dicts[key].append(value)
            elif not key:
                all_data.append(value)

        # store the parents we have already delt with
        computed_parents = [False]

        while len(computed_parents) != len(groupby_dicts.keys()) + 1:
            for k in groupby_dicts:
                if k in computed_parents:
                    continue
                v = list(groupby_dicts[k])
                if all_data:
                    for rec in all_data:
                        if rec['id'] == k:
                            all_data = all_data[:all_data.index(
                                rec)] + list(v)[::-1] + \
                                all_data[all_data.index(rec):]

                            computed_parents.append(k)

                if not all_data:
                    all_data = list(v)

        all_data = all_data[::-1]

        return {'cols': keys, 'fields_names': fields_names,
                'fields_types': fields_types, 'all_data': all_data}
