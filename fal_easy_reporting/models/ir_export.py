# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ir_export(models.Model):
    _inherit = 'ir.exports'

    model_id = fields.Many2one('ir.model', string="Model")

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.resource = self.model_id.model


class ir_exports_line(models.Model):
    _name = 'ir.exports.line'
    _inherit = 'ir.exports.line'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', help="Used to order the sequences.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
