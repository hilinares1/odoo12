# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv.expression import get_unaccent_wrapper


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fal_shortname = fields.Char(
        "Short name",
        index=True
    )

    @api.multi
    def name_get(self):
        res = super(ResPartner, self).name_get()
        for index, partner in enumerate(res, start=0):
            # If it's not in odoo custom format
            if not (self._context.get('show_address_only') or self._context.get('show_address') or self._context.get('show_email') or self._context.get('html_format')):
                name = partner[1]
                partner_obj = self.browse(partner[0])
                # Change if res are company / partner with parent company
                if partner_obj.company_name or partner_obj.parent_id:
                    if not partner_obj.is_company:
                        name = "%s, %s" % (partner_obj.parent_id.fal_shortname or partner_obj.commercial_company_name or partner_obj.parent_id.name, partner_obj.name or '')
                if partner_obj.is_company:
                    name = partner_obj.fal_shortname or partner_obj.name or ''
                partner = (partner[0], name)
                res[index] = partner
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(ResPartner, self).name_search(name, args, operator, limit)
        if args is None:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            where_query = self._where_calc(args)
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or ' WHERE '

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
                         FROM res_partner
                      {where} ({fal_shortname} {operator} {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(where=where_str,
                               operator=operator,
                               fal_shortname=unaccent('fal_shortname'),
                               display_name=unaccent('display_name'),
                               percent=unaccent('%s'),)

            where_clause_params += [search_name]*2
            if limit:
                query += ' limit %s'
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)
            partner_ids = [row[0] for row in self.env.cr.fetchall()]
            super_partner_ids = []
            for partner_id in res:
                if partner_id[0] not in partner_ids:
                    partner_ids.append(partner_id[0])
            if partner_ids:
                return self.browse(partner_ids).name_get()
            else:
                return []
        return super(ResPartner, self).name_search(name, args, operator=operator, limit=limit)

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'fal_shortname', 'parent_id.fal_shortname')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()