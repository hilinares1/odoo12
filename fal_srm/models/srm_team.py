# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from babel.dates import format_date
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import json
from odoo.tools.safe_eval import safe_eval

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SrmTeam(models.Model):
    _name = "srm.team"
    _inherit = ['mail.thread']
    _description = "Purchasing Team"
    _order = "name"

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        company_id = self.sudo(user_id).env.user.company_id.id
        team_id = self.env['srm.team'].sudo().search([
            '|', ('user_id', '=', user_id), ('member_ids', '=', user_id),
            '|', ('company_id', '=', False), ('company_id', 'child_of', [company_id])
        ], limit=1)
        if not team_id and 'default_team_id' in self.env.context:
            team_id = self.env['srm.team'].browse(self.env.context.get('default_team_id'))
        return team_id

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_your_pipeline(self):
        action = self.env.ref('fal_srm.srm_proposal_agreements_tree_view').read()[0]
        user_team_id = self.env.user.purchase_team_id.id
        if not user_team_id:
            user_team_id = self.search([], limit=1).id
            action['help'] = _("""<p class='o_view_nocontent_smiling_face'>Add new agreements</p><p>
    Looks like you are not a member of a purchase Team. You should add yourself
    as a member of one of the Purchase Team.
</p>""")
            if user_team_id:
                action['help'] += "<p>As you don't belong to any Purchase Team, Odoo opens the first one by default.</p>"

        action_context = safe_eval(action['context'], {'uid': self.env.uid})
        if user_team_id:
            action_context['default_team_id'] = user_team_id

        action['context'] = action_context
        return action

    use_proposals = fields.Boolean('Proposals', help="Check this box to filter and qualify incoming requests as proposal before converting them into agreement and assigning them to a purchaser.")
    use_agreements = fields.Boolean('Pipeline', help="Check this box to manage a prepurchases process with agreements.")
    name = fields.Char('Purchase Team', required=True, translate=True)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the Purchase Team without removing it.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get('srm.team'))
    currency_id = fields.Many2one(
        "res.currency", related='company_id.currency_id',
        string="Currency", readonly=True)
    user_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.One2many('res.users', 'purchase_team_id', string='Channel Members')
    favorite_user_ids = fields.Many2many(
        'res.users', 'srm_team_favorite_user_rel', 'team_id', 'user_id',
        string='Favorite Members',
        default=_get_default_favorite_user_ids)
    is_favorite = fields.Boolean(
        string='Show on dashboard',
        compute='_compute_is_favorite', inverse='_inverse_is_favorite',
        help="Favorite teams to display them in the dashboard and access them easily.")
    reply_to = fields.Char(string='Reply-To',
                           help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this Purchase Team")
    color = fields.Integer(string='Color Index', help="The color of the channel")
    team_type = fields.Selection([('purchase', 'Purchase'), ('website', 'Website')], string='Team Type', default='purchase', required=True,
                                 help="The type of this channel, it will define the resources this channel uses.")

    def _compute_is_favorite(self):
        for team in self:
            team.is_favorite = self.env.user in team.favorite_user_ids

    def _inverse_is_favorite(self):
        sudoed_self = self.sudo()
        to_fav = sudoed_self.filtered(lambda team: self.env.user not in team.favorite_user_ids)
        to_fav.write({'favorite_user_ids': [(4, self.env.uid)]})
        (sudoed_self - to_fav).write({'favorite_user_ids': [(3, self.env.uid)]})
        return True
