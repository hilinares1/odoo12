# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class fal_vprocess(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    #_order = "sequence"

    _name = "fal.vprocess"
    _description = "Validation Process"

    name = fields.Char("Name", default="Process")
    active = fields.Boolean("Active", default=True)
    
    # @TODO this field is useless as we put the option on the step instead
    disable_edit = fields.Boolean("Disable Edition", default=True)
    
    
    disable_actions = fields.Boolean("Disable Actions", default=True)
    allowed_actions_list = fields.Char("Allowed actions names", default="")
    
    allow_restart_after_approved = fields.Boolean("Allow restart after approved if triggered", default=False)
    allow_restart_after_cancelled = fields.Boolean("Allow restart after cancelled if triggered", default=False)
    
    log_message_to_object = fields.Boolean("Log messages to object", default=False)
    process_activity_type_id = fields.Many2one('mail.activity.type', 'Activity type', required=False)
    
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    model_name = fields.Char(string='Model name', related='model_id.model')
    
    trigger_id = fields.Many2one('ir.filters', 'Trigger', required=True)
    trigger_domain = fields.Text(string='Trigger domain', related='trigger_id.domain')
    
    filter_id = fields.Many2one('ir.filters', 'Process-wide filter', required=True)
    filter_domain = fields.Text(string='Process-wide domain', related='filter_id.domain')
    
    step_ids = fields.One2many("fal.vprocess.step", 'process_id', 'Steps', ondelete="cascade")
