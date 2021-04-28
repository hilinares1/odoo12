# -*- coding: utf-8 -*-

from odoo import api, models


class CrmLeadLostAndCreatePartner(models.TransientModel):
    _name = 'crm.lead.lost.and.partner.binding'
    _inherit = ['crm.lead.lost', 'crm.partner.binding']
    _description = "Lost Lead and Create Partner"

    @api.multi
    def action_lost_and_create_partner(self):
        self.ensure_one()
        values = {}
        # Manage the partner assignation
        if self.partner_id:
            values['partner_id'] = self.partner_id.id

        leads = self.env['crm.lead'].browse(self._context.get('active_ids', []))
        for lead in leads:
            partner_id = self._create_partner(
                lead.id, self.action, values.get('partner_id'))
            lead.partner_id = partner_id
        # Make it a lost lead
        leads.write({'lost_reason': self.lost_reason_id.id})
        return leads.action_set_lost()

    def _create_partner(self, lead_id, action, partner_id):
        """ Create partner based on action.
            :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        result = self.env['crm.lead'].browse(lead_id).handle_partner_assignation(action, partner_id)
        return result.get(lead_id)
