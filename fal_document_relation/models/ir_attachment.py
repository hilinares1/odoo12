# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _get_available_models(self):
    	available_models = self.env['ir.model'].search([])
    	return [(x.model, x.model) for x in available_models]

    fal_record_ref = fields.Reference(selection=_get_available_models, string="Related Record")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
        	# set res_id and res_model based on fal_record_ref
	        if 'fal_record_ref' in vals:
	        	vals['res_model'], vals['res_id'] = vals['fal_record_ref'].split(',')
        return super(IrAttachment, self).create(vals_list)

    @api.multi
    def write(self, vals):
        if 'fal_record_ref' in vals:
        	vals['res_model'], vals['res_id'] = vals['fal_record_ref'].split(',')
        return super(IrAttachment, self).write(vals)
