# -*- coding: utf-8 -*-

import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def _compute_potential_dupplicates(self):
        """
        The method to compute potential_dupplicates and duplicates_count
        """
        for record in self:
            potential_dupplicates = False
            duplicates_count = 0

            fields = self.env.user.company_id.duplicate_fields_partner_soft
            domain = [('id', '!=', record.id)]
            # --- Support Multi Companies: duplicates are possible between different companies --- #
            if record.company_id:
                domain.append(('company_id', '=', record.company_id.id))
            # --- Construct Domain by all criteria from settings --- #
            or_operators_number = -1
            domain_temp = []
            for field in fields:
                if field.ttype in ('one2many', 'many2many', 'binary', 'reference', 'serialized'):
                    _logger.warning("Inacceptable field type %s", field.ttype)
                elif field.ttype in ('many2one', 'one2many', 'many2many'):
                    if record[field.name]:
                        domain_temp.append((field.name, 'in', record[field.name].ids))
                        or_operators_number += 1
                elif field.ttype in ('char'):
                    if record[field.name]:
                        domain_temp.append((field.name, 'ilike', record[field.name]))
                        or_operators_number += 1
                elif record[field.name]:
                    domain_temp.append((field.name, '=', record[field.name]))
                    or_operators_number += 1

            if or_operators_number != -1:  # Otherwise, it means domain consists only of company_id or it is empty
                if or_operators_number > 0:
                    domain += ['|'] * or_operators_number
                domain += domain_temp
                _logger.info("Soft duplicate leads are searched by the domain %s", domain)
                duplicate_parts = record.search(domain)
                if duplicate_parts:
                    potential_dupplicates = [(6, 0, duplicate_parts.ids)]
                    duplicates_count = len(duplicate_parts)

            record.potential_dupplicates = potential_dupplicates
            record.duplicates_count = duplicates_count

    @api.model
    def search_duplicates_count(self, operator, value):
        """
        Search method for duplicates_count
        Introduced since the field is not stored
        """
        leads = self.search([])
        potential_dupplicates = []
        for lead in leads:
            if lead.duplicates_count > 0:
                potential_dupplicates.append(lead.id)
        return [('id', 'in', potential_dupplicates)]


    potential_dupplicates = fields.Many2many(
        'res.partner',
        'rel_table',
        'partner_1',
        'partner_2',
        string='Potential duplicates',
        compute=_compute_potential_dupplicates,
    )
    duplicates_count = fields.Integer(
        string='Duplicates Count',
        compute=_compute_potential_dupplicates,
        search='search_duplicates_count',
    )

    @api.model
    def create(self, values):
        """
        Overwrite to force 'write' in 'create'
        """
        partner_id = super(res_partner, self).create(values)
        partner_id.write({})
        return partner_id

    @api.multi
    def write(self, vals):
        """
        Overwrite to check for rigids duplicates and raise UserError in such a case
        """
        for record in self:
            partner_id = super(res_partner, record).write(vals)

            fields = record.env.user.company_id.duplicate_fields_partner
            domain = [('id', '!=', record.id)]
            # --- Support Multi Companies: duplicates are possible between different companies --- #
            if record.company_id:
                domain.append(('company_id', '=', record.company_id.id))
            # --- Construct Domain by all criteria from settings --- #
            or_operators_number = -1
            domain_temp = []
            for field in fields:
                if field.ttype in ('one2many', 'many2many', 'binary', 'reference', 'serialized'):
                    _logger.warning("Inacceptable field type %s", field.ttype)
                elif field.ttype in ('many2one', 'one2many', 'many2many'):
                    if record[field.name]:
                        domain_temp.append((field.name, 'in', record[field.name].ids))
                        or_operators_number += 1
                elif record[field.name]:
                    domain_temp.append((field.name, '=', record[field.name]))
                    or_operators_number += 1

            if or_operators_number != -1:  # Otherwise, it means domain consists only of company_id or it is empty
                if or_operators_number > 0:
                    domain += ['|'] * or_operators_number
                domain += domain_temp
                _logger.info("Duplicate partners are searched by the domain %s", domain)
                duplicate_partners = record.search(domain)
            else:
                return partner_id

            if len(duplicate_partners) == 0:
                return partner_id
            else:
                _logger.info("Duplicate partners number is %s", len(duplicate_partners))
                warning = _('Duplicates were found: \n')
                for duplicate in duplicate_partners:
                    warning += '"[ID '+str(duplicate.id) + '] ' + duplicate.name+'"' + _(' by fields: ')
                    for field in fields:
                        if record[field.name] and record[field.name] == duplicate[field.name]:
                            warning += field.name + ' - ' + record[field.name] + '; '
                    warning += '\n'
                raise exceptions.UserError(warning)

    @api.multi
    def open_duplicates(self):
        """
        The method to open tree of potential duplicates
        """
        for part in self:
            return {
                'name': 'Duplicates',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'res.partner',
                'domain': [('id', 'in', part.potential_dupplicates.ids)],
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
            }
