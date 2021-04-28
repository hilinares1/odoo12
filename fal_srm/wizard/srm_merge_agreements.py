# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MergeAgreement(models.TransientModel):
    _name = 'srm.merge.agreement'
    _description = 'Merge Agreements'

    @api.model
    def default_get(self, fields):
        record_ids = self._context.get('active_ids')
        result = super(MergeAgreement, self).default_get(fields)

        if record_ids:
            if 'agreement_ids' in fields:
                agree_ids = self.env['srm.proposal'].browse(record_ids).filtered(lambda agree: agree.probability < 100).ids
                result['agreement_ids'] = agree_ids

        return result

    agreement_ids = fields.Many2many('srm.proposal', 'merge_agreement_rel', 'merge_id', 'agreement_id', string='Proposal/Agreements')
    user_id = fields.Many2one('res.users', 'Responsible', index=True)
    team_id = fields.Many2one('srm.team', 'Purchase Team', oldname='section_id', index=True)

    @api.multi
    def action_merge(self):
        self.ensure_one()
        merge_agreement = self.agreement_ids.merge_agreement(self.user_id.id, self.team_id.id)

        # The newly created proposal might be a proposal or an agreements: redirect toward the right view
        if merge_agreement.type == 'agreement':
            return merge_agreement.redirect_agreement_view()
        else:
            return merge_agreement.redirect_proposal_view()

    @api.onchange('user_id')
    def _onchange_user(self):
        """ When changing the user, also set a team_id or restrict team id
            to the ones user_id is member of. """
        team_id = False
        if self.user_id:
            user_in_team = False
            if self.team_id:
                user_in_team = self.env['srm.team'].search_count([('id', '=', self.team_id.id), '|', ('user_id', '=', self.user_id.id), ('member_ids', '=', self.user_id.id)])
            if not user_in_team:
                team_id = self.env['srm.team'].search(['|', ('user_id', '=', self.user_id.id), ('member_ids', '=', self.user_id.id)], limit=1)
        self.team_id = team_id
