# -*- coding: utf-8 -*-
from odoo import models, fields, api


class add_deposit_wizard(models.TransientModel):
    _name = "fal.block.wizard"
    _description = "block Wizard"

    notes = fields.Text(string="Notes")
    fal_working_machine = fields.Boolean(
        string="Using Working Machine", related="loss_id.fal_working_machine")
    loss_id = fields.Many2one(
        'mrp.workcenter.productivity.loss', "Loss Reason",
        ondelete='restrict')
    loss_type = fields.Selection(
        "Effectiveness", related='loss_id.loss_type', store=True)
    fal_workshop_id = fields.Many2one(
        'mrp.workcenter', string='Working Machine'
    )
    workshop_ids = fields.Many2many('mrp.workcenter', string="Workshop")

    @api.multi
    def block(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        mrp_obj = self.env['mrp.production']
        mrp = mrp_obj.browse(active_id)
        for item in self:
            last = mrp.fal_tracking_ids.filtered(lambda r: not r.end_hour)
            last.sorted(key=lambda r: r.id, reverse=True)
            if last:
                last[0].write({
                    'loss_id': item.loss_id.id,
                    'loss_type': item.loss_type,
                    'fal_workshop_id': item.fal_workshop_id.id,
                    'notes': item.notes,
                })
            mrp.write({'fal_tracking_state': 'blocked'})
