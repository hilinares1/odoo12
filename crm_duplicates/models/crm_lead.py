# -*- coding: utf-8 -*-

import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class crm_lead(models.Model):
    _inherit = "crm.lead"

    @api.multi
    def _compute_potential_dupplicates(self):
        """
        The method to compute potential_dupplicates and duplicates_count
        """
        for record in self:
            potential_dupplicates = False
            duplicates_count = 0

            fields = self.env.user.company_id.duplicate_fields_lead_soft
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
                    if len(record[field.name]) > 0:
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
                _logger.info("Soft duplicate partners are searched by the domain %s", domain)
                duplicate_leads = record.search(domain)
                if duplicate_leads:
                    potential_dupplicates = [(6, 0, duplicate_leads.ids)]
                    duplicates_count = len(duplicate_leads)

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
        'crm.lead',
        'rel_table',
        'leadx_1',
        'leady_2',
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
        lead_id = super(crm_lead, self).create(values)
        lead_id.write({})
        return lead_id

    @api.multi
    def merge_opportunity(self, user_id=False, team_id=False):
        """
        Overwrite to pass context and let merge duplicats
        """
        context = {
            'inhibit_duplication_warning': True,
        }
        return super(crm_lead, self.with_context(context)).merge_opportunity(user_id=user_id, team_id=team_id)

    @api.multi
    def write(self, vals):
        """
        Overwrite to check for rigids duplicates and raise UserError in such a case
        """
        if self._context.get('inhibit_duplication_warning'):
            return super(crm_lead, self).write(vals)

        for lead in self:
            lead_id = super(crm_lead, lead).write(vals)

            fields = self.env.user.company_id.duplicate_fields_lead
            domain = [('id', '!=', lead.id)]
            # --- Support Multi Companies: duplicates are possible between different companies --- #
            if lead.company_id:
                domain.append(('company_id', '=', lead.company_id.id))
            # --- Construct Domain by all criteria from settings --- #
            or_operators_number = -1
            domain_temp = []
            for field in fields:
                if field.ttype in ['one2many', 'many2many', 'binary', 'reference', 'serialized']:
                    _logger.warning("Inacceptable field type %s", field.ttype)
                elif field.ttype in ['many2one', 'one2many', 'many2many']:
                    if len(lead[field.name]) > 0:
                        domain_temp.append((field.name, 'in', lead[field.name].ids))
                        or_operators_number += 1
                elif lead[field.name]:
                    domain_temp.append((field.name, '=', lead[field.name]))
                    or_operators_number += 1

            if or_operators_number != -1:  # Otherwise, it means domain consists only of company_id or it is empty
                if or_operators_number > 0:
                    domain += ['|'] * or_operators_number
                domain += domain_temp
                _logger.info("Duplicate partners are searched by the domain %s", domain)
                duplicate_leads = lead.search(domain)
            else:
                return lead_id

            if len(duplicate_leads) == 0:
                return lead_id
            else:
                _logger.info("Duplicate leads number is %s", len(duplicate_leads))
                warning = _('Duplicates were found: \n')
                for duplicate in duplicate_leads:
                    warning += '"[ID '+str(duplicate.id) + '] ' + duplicate.name+'"' + _(' by fields: ')
                    for field in fields:
                        if lead[field.name] and lead[field.name] == duplicate[field.name]:
                            warning += field.name + ' - ' + lead[field.name] + '; '
                    warning += '\n'
                raise exceptions.UserError(warning)

    @api.multi
    def open_duplicates(self):
        """
        The method to open tree of potential duplicates
        """
        for lead in self:
            res = {
                'name': 'Duplicates',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'view_id': False,
                'res_model': 'crm.lead',
                'domain': str([('id', 'in', lead.potential_dupplicates.ids)]),
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'context': {
                    'form_view_ref': 'crm_duplicates.crm_case_form_view_oppor',
                },
            }
        return res
