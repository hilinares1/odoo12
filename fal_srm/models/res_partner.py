# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Partner(models.Model):

    _inherit = 'res.partner'

    srm_team_id = fields.Many2one('srm.team', string='Supplier Team')
    srm_proposal_ids = fields.One2many('srm.proposal', 'partner_id', string='Proposal', domain=[('type', '=', 'agreement')])
    srm_proposal_count = fields.Integer("Proposal", compute='_compute_proposal_count')

    @api.model
    def default_get(self, fields):
        rec = super(Partner, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        if active_model == 'srm.proposal':
            proposal = self.env[active_model].browse(self.env.context.get('active_id')).exists()
            if proposal:
                rec.update(
                    phone=proposal.phone,
                    mobile=proposal.mobile,
                    function=proposal.function,
                    title=proposal.title.id,
                    website=proposal.website,
                    street=proposal.street,
                    street2=proposal.street2,
                    city=proposal.city,
                    state_id=proposal.state_id.id,
                    country_id=proposal.country_id.id,
                    zip=proposal.zip,
                )
        return rec

    @api.multi
    def _compute_proposal_count(self):
        for partner in self:
            operator = 'child_of' if partner.is_company else '='  # the opportunity count should counts the opportunities of this company and all its contacts
            partner.srm_proposal_count = self.env['srm.proposal'].search_count([('partner_id', operator, partner.id), ('type', '=', 'agreement')])
