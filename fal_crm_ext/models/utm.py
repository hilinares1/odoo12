# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID
from odoo.http import request
from odoo.tools import pycompat
from odoo.tools.safe_eval import safe_eval


class Campaign(models.Model):
    _name = "utm.campaign"
    _inherit = ['mail.alias.mixin', 'utm.campaign']

    crm_team_id = fields.Many2one('crm.team', string="CRM Team")
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True, help="The email address associated with this campaign. New emails received will automatically create new leads assigned to the campaign.")

    @api.multi
    def write(self, vals):
        result = super(Campaign, self).write(vals)
        for team in self:
            team.alias_id.write(team.get_alias_values())
        return result

    def get_alias_values(self):
        has_group_use_lead = self.env.user.has_group('crm.group_use_lead')
        values = super(Campaign, self).get_alias_values()
        values['alias_defaults'] = defaults = safe_eval(self.alias_defaults or "{}")
        defaults['type'] = 'lead' if has_group_use_lead and self.crm_team_id and self.crm_team_id.use_leads else 'opportunity'
        defaults['team_id'] = self.crm_team_id and self.crm_team_id.id or False
        defaults['campaign_id'] = self.id
        return values

    def get_alias_model_name(self, vals):
        """ Return the model name for the alias. Incoming emails that are not
            replies to existing records will cause the creation of a new record
            of this alias model. The value may depend on ``vals``, the dict of
            values passed to ``create`` when a record of this model is created.
        """
        return 'crm.lead'
