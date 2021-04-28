# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_srm_proposal_created = fields.Boolean('New Agreement')
    kpi_srm_proposal_created_value = fields.Integer(compute='_compute_kpi_srm_proposal_created_value')
    kpi_srm_agreements_won = fields.Boolean('Agreements Won')
    kpi_srm_agreements_won_value = fields.Integer(compute='_compute_kpi_srm_agreements_won_value')

    def _compute_kpi_srm_proposal_created_value(self):
        if not self.env.user.has_group('purchase.group_purchase_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            record.kpi_srm_proposal_created_value = self.env['srm.proposal'].search_count([
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id)
            ])

    def _compute_kpi_srm_agreements_won_value(self):
        if not self.env.user.has_group('purchase.group_purchase_user'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            record.kpi_srm_agreements_won_value = self.env['srm.proposal'].search_count([
                ('type', '=', 'agreement'),
                ('probability', '=', '100'),
                ('date_closed', '>=', start),
                ('date_closed', '<', end),
                ('company_id', '=', company.id)
            ])

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res['kpi_srm_proposal_created'] = 'fal_srm.srm_proposal_agreements_tree_view&menu_id=%s' % self.env.ref('fal_srm.srm_menu_root').id
        res['kpi_srm_agreement_won'] = 'fal_srm.srm_proposal_agreements_tree_view&menu_id=%s' % self.env.ref('fal_srm.srm_menu_root').id
        if user.has_group('fal_srm.group_use_lead'):
            res['kpi_srm_proposal_created'] = 'fal_srm.srm_proposal_all_proposals&menu_id=%s' % self.env.ref('fal_srm.srm_menu_root').id
        return res
