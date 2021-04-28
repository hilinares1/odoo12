# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Proposal2AgreementPartner(models.TransientModel):

    _name = 'srm.proposal2agreement.partner'
    _description = 'Convert Proposal to Agreement (not in mass)'
    _inherit = 'srm.partner.binding'

    @api.model
    def default_get(self, fields):
        """ Default get for name, opportunity_ids.
            If there is an exisitng partner link to the lead, find all existing
            opportunities links with this partner to merge all information together
        """
        result = super(Proposal2AgreementPartner, self).default_get(fields)
        if self._context.get('active_id'):
            tomerge = {int(self._context['active_id'])}

            partner_id = result.get('partner_id')
            proposal = self.env['srm.proposal'].browse(self._context['active_id'])
            email = proposal.partner_id.email if proposal.partner_id else proposal.email_from

            tomerge.update(self._get_duplicated_proposals(partner_id, email, include_lost=True).ids)

            if 'action' in fields and not result.get('action'):
                result['action'] = 'exist' if partner_id else 'create'
            if 'partner_id' in fields:
                result['partner_id'] = partner_id
            if 'name' in fields:
                result['name'] = 'merge' if len(tomerge) >= 2 else 'convert'
            if 'agreement_ids' in fields and len(tomerge) >= 2:
                result['agreement_ids'] = list(tomerge)
            if proposal.user_id:
                result['user_id'] = proposal.user_id.id
            if proposal.team_id:
                result['team_id'] = proposal.team_id.id
            if not partner_id and not proposal.contact_name:
                result['action'] = 'nothing'
        return result

    name = fields.Selection([
        ('convert', 'Convert to agreement'),
        ('merge', 'Merge with existing Agreements')
    ], 'Conversion Action', required=True)
    agreement_ids = fields.Many2many('srm.proposal', string='Agreements')
    user_id = fields.Many2one('res.users', 'Responsible', index=True)
    team_id = fields.Many2one('srm.team', 'Purchase Team', oldname='section_id', index=True)

    @api.onchange('action')
    def onchange_action(self):
        if self.action == 'exist':
            self.partner_id = self._find_matching_partner()
        else:
            self.partner_id = False

    @api.onchange('user_id')
    def _onchange_user(self):
        """ When changing the user, also set a team_id or restrict team id
            to the ones user_id is member of.
        """
        if self.user_id:
            if self.team_id:
                user_in_team = self.env['srm.team'].search_count([('id', '=', self.team_id.id), '|', ('user_id', '=', self.user_id.id), ('member_ids', '=', self.user_id.id)])
            else:
                user_in_team = False
            if not user_in_team:
                values = self.env['srm.proposal']._onchange_user_values(self.user_id.id if self.user_id else False)
                self.team_id = values.get('team_id', False)

    @api.model
    def _get_duplicated_proposals(self, partner_id, email, include_lost=False):
        return self.env['srm.proposal']._get_duplicated_proposal_by_emails(partner_id, email, include_lost=include_lost)

    # NOTE JEM : is it the good place to test this ?
    @api.model
    def view_init(self, fields):
        """ Check some preconditions before the wizard executes. """
        for proposal in self.env['srm.proposal'].browse(self._context.get('active_ids', [])):
            if proposal.probability == 100:
                raise UserError(_("Closed/Dead proposals cannot be converted into agreements."))
        return False

    @api.multi
    def _convert_agreement(self, vals):
        self.ensure_one()

        res = False

        proposals = self.env['srm.proposal'].browse(vals.get('proposal_ids'))
        for proposal in proposals:
            self_def_user = self.with_context(default_user_id=self.user_id.id)
            partner_id = self_def_user._create_partner(
                proposal.id, self.action, vals.get('partner_id') or proposal.partner_id.id)
            res = proposal.convert_agreement(partner_id, [], False)
        user_ids = vals.get('user_ids')

        proposals_to_allocate = proposals
        if self._context.get('no_force_assignation'):
            proposals_to_allocate = proposals_to_allocate.filtered(lambda proposal: not proposal.user_id)

        if user_ids:
            proposals_to_allocate.allocate_responsible(user_ids, team_id=(vals.get('team_id')))

        return res

    @api.multi
    def action_apply(self):
        """ Convert lead to opportunity or merge lead and opportunity and open
            the freshly created opportunity view.
        """
        self.ensure_one()
        values = {
            'team_id': self.team_id.id,
        }

        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        if self.name == 'merge':
            proposals = self.with_context(active_test=False).agreement_ids.merge_agreement()
            if not proposals.active:
                proposals.write({'active': True, 'activity_type_id': False, 'lost_reason': False})
            if proposals.type == "proposal":
                values.update({'proposal_ids': proposals.ids, 'user_ids': [self.user_id.id]})
                self.with_context(active_ids=proposals.ids)._convert_agreement(values)
            elif not self._context.get('no_force_assignation') or not proposals.user_id:
                values['user_id'] = self.user_id.id
                proposals.write(values)
        else:
            proposals = self.env['srm.proposal'].browse(self._context.get('active_ids', []))
            values.update({'proposal_ids': proposals.ids, 'user_ids': [self.user_id.id]})
            self._convert_agreement(values)

        return proposals[0].redirect_agreement_view()

    def _create_partner(self, proposal_id, action, partner_id):
        """ Create partner based on action.
            :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by Lead2OpportunityPartner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        if action == 'each_exist_or_create':
            partner_id = self.with_context(active_id=proposal_id)._find_matching_partner()
            action = 'create'
        result = self.env['srm.proposal'].browse(proposal_id).handle_partner_assignation(action, partner_id)
        return result.get(proposal_id)


class Proposal2AgreementMassConvert(models.TransientModel):

    _name = 'srm.proposal2agreement.partner.mass'
    _description = 'Convert Proposal to Agreement (in mass)'
    _inherit = 'srm.proposal2agreement.partner'

    @api.model
    def default_get(self, fields):
        res = super(Proposal2AgreementMassConvert, self).default_get(fields)
        if 'partner_id' in fields:  # avoid forcing the partner of the first lead as default
            res['partner_id'] = False
        if 'action' in fields:
            res['action'] = 'each_exist_or_create'
        if 'name' in fields:
            res['name'] = 'convert'
        if 'agreement_ids' in fields:
            res['agreement_ids'] = False
        return res

    user_ids = fields.Many2many('res.users', string='Responsible')
    team_id = fields.Many2one('srm.team', 'Purchase Team', index=True, oldname='section_id')
    deduplicate = fields.Boolean('Apply deduplication', default=True, help='Merge with existing proposals/agreement of each partner')
    action = fields.Selection([
        ('each_exist_or_create', 'Use existing partner or create'),
        ('nothing', 'Do not link to a vendor')
    ], 'Related Customer', required=True)
    force_assignation = fields.Boolean('Force assignation', help='If unchecked, this will leave the salesman of duplicated agreement')

    @api.onchange('action')
    def _onchange_action(self):
        if self.action != 'exist':
            self.partner_id = False

    @api.onchange('deduplicate')
    def _onchange_deduplicate(self):
        active_proposals = self.env['srm.proposal'].browse(self._context['active_ids'])
        partner_ids = [(proposal.partner_id.id, proposal.partner_id and proposal.partner_id.email or proposal.email_from) for proposal in active_proposals]
        partners_duplicated_proposals = {}
        for partner_id, email in partner_ids:
            duplicated_proposals = self._get_duplicated_proposals(partner_id, email)
            if len(duplicated_proposals) > 1:
                partners_duplicated_proposals.setdefault((partner_id, email), []).extend(duplicated_proposals)

        proposals_with_duplicates = []
        for proposal in active_proposals:
            proposal_tuple = (proposal.partner_id.id, proposal.partner_id.email if proposal.partner_id else proposal.email_from)
            if len(partners_duplicated_proposals.get(proposal_tuple, [])) > 1:
                proposals_with_duplicates.append(proposal.id)

        self.agreement_ids = self.env['srm.proposal'].browse(proposals_with_duplicates)

    @api.multi
    def _convert_agreement(self, vals):
        self.ensure_one()
        purchaseteam_id = self.team_id.id if self.team_id else False
        responsible_ids = []
        if self.user_ids:
            responsible_ids = self.user_ids.ids
        vals.update({'user_ids': responsible_ids, 'team_id': purchaseteam_id})
        return super(Proposal2AgreementMassConvert, self)._convert_agreement(vals)

    @api.multi
    def mass_convert(self):
        self.ensure_one()
        if self.name == 'convert' and self.deduplicate:
            merged_proposal_ids = set()
            remaining_proposal_ids = set()
            proposal_selected = self._context.get('active_ids', [])
            for proposal_id in proposal_selected:
                if proposal_id not in merged_proposal_ids:
                    proposal = self.env['srm.proposal'].browse(proposal_id)
                    duplicated_proposals = self._get_duplicated_proposals(proposal.partner_id.id, proposal.partner_id.email if proposal.partner_id else proposal.email_from)
                    if len(duplicated_proposals) > 1:
                        proposal = duplicated_proposals.merge_agreement()
                        merged_proposal_ids.update(duplicated_proposals.ids)
                        remaining_proposal_ids.add(proposal.id)
            active_ids = set(self._context.get('active_ids', {}))
            active_ids = (active_ids - merged_proposal_ids) | remaining_proposal_ids

            self = self.with_context(active_ids=list(active_ids))  # only update active_ids when there are set
        no_force_assignation = self._context.get('no_force_assignation', not self.force_assignation)
        return self.with_context(no_force_assignation=no_force_assignation).action_apply()
