# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class fal_vprocess_rule(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    _name = "fal.vprocess.rule"
    _description = "Rule"

    name = fields.Char("Name", default="Rule")
    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer("Sequence", default=0)
    
    step_id = fields.Many2one('fal.vprocess.step', 'Step', auto_join=True)
    user_ids = fields.Many2many('res.users')
    user_filter_id = fields.Many2one('ir.filters', 'User Filter', required=False)
    user_filter_domain = fields.Text(string='Domain', related='user_filter_id.domain')
    
    custom_user_domain = fields.Text(string='Custom user domain')
    
    filter_id = fields.Many2one('ir.filters', 'Applies on', required=True)
    domain = fields.Text(string='Domain', related='filter_id.domain')
