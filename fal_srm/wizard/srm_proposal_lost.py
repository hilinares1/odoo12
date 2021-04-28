# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SrmLeadLost(models.TransientModel):
    _name = 'srm.proposal.lost'
    _description = 'Get Lost Reason'

    lost_reason_id = fields.Many2one('srm.lost.reason', 'Lost Reason')

    @api.multi
    def action_lost_reason_apply(self):
        leads = self.env['srm.proposal'].browse(self.env.context.get('active_ids'))
        leads.write({'lost_reason': self.lost_reason_id.id})
        return leads.action_set_lost()
