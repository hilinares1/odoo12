# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        if self.env.context.get('default_fal_srm_agreement_id'):
            self = self.with_context(
                default_res_model_id=self.env.ref('fal_srm.model_srm_proposal').id,
                default_res_id=self.env.context['default_fal_srm_agreement_id']
            )
        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to opportunity id (aka creating meeting from lead chatter)
        if 'fal_srm_agreement_id' not in defaults and defaults.get('res_id') and (defaults.get('res_model') or defaults.get('res_model_id')):
            if (defaults.get('res_model') and defaults['res_model'] == 'srm.proposal') or (defaults.get('res_model_id') and self.env['ir.model'].sudo().browse(defaults['res_model_id']).model == 'srm.proposal'):
                defaults['fal_srm_agreement_id'] = defaults['res_id']

        return defaults

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        if self.env.context.get('active_model') == 'srm.proposal':
            fal_srm_agreement_id = self.env.context.get('active_id')
            for event in self:
                if event.fal_srm_agreement_id.id == fal_srm_agreement_id:
                    event.is_highlighted = True

    fal_srm_agreement_id = fields.Many2one('srm.proposal', 'supplier Opportunity', domain="[('type', '=', 'agreement')]")

    @api.model
    def create(self, vals):
        event = super(CalendarEvent, self).create(vals)

        if event.fal_srm_agreement_id and not event.activity_ids:
            event.fal_srm_agreement_id.log_meeting(event.name, event.start, event.duration)
        return event
