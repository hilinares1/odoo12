from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    fal_type = fields.Selection(
        [('routing', 'Routing Work Center'), ('working', 'Workshop Machine')],
        string='Type', default='routing'
    )
    fal_workshop_ids = fields.Many2many(
        'mrp.workcenter', 'workshop_routing_machines_rel',
        'route_workcenter_id', 'workshop_workcenter_id',
        string='Workshop Machine',
        domain=[('fal_type', '=', 'working')]
    )


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    fal_wokrshop_id = fields.Many2one(
        'mrp.workcenter', string='Working Machine',
    )
    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Routing Work Center'
    )
    fal_available_workshop_ids = fields.Many2many(
        relation='mrp.workcenter', related='workcenter_id.fal_workshop_ids',
    )


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    workcenter_id = fields.Many2one(
        'mrp.workcenter', string='Routing Work Center'
    )
    fal_wokrshop_id = fields.Many2one(
        'mrp.workcenter', string='Working Machine',
    )
    fal_available_workshop_ids = fields.Many2many(
        relation='mrp.workcenter', related='workcenter_id.fal_workshop_ids',
    )

    @api.model
    def create(self, vals):
        res = super(MrpWorkOrder, self).create(vals)
        if not res.fal_wokrshop_id:
            res.write({'state': 'pending'})
        return res

    @api.multi
    def button_start(self):
        res = super(MrpWorkOrder, self).button_start()
        if not self.fal_wokrshop_id:
            raise UserError(_("Please fill in working machine for this work order before continue."))
        return res

    @api.multi
    def record_production(self):
        res = super(MrpWorkOrder, self).record_production()
        if not self.fal_wokrshop_id:
            raise UserError(_("Please fill in working machine for this work order before continue."))
        return res

    @api.multi
    def fal_set_ready(self):
        for wo in self:
            wo.write({'state': 'ready'})
