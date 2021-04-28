# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ResPartner(models.Model):    
    _name = "res.partner"
    _inherit = ['res.partner','mail.thread', 'mail.activity.mixin']
    
    attn = fields.Char('Attention',size=64)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
