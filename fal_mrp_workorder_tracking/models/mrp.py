from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fal_tracking_type = fields.Selection(
        [
            ('none', 'No Time Tracking'),
            ('routing', 'On Routing and by Quantity'),
            ('workorder', 'On Workorder and by Start-Stop')
        ],
        string='Time Tracking Type',
        default='routing',
    )
    fal_tracking_ids = fields.One2many(
        'fal.mrp.production.tracking',
        'mrp_id',
        string='Manufacturing Order Time Tracking'
    )
    fal_tracking_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('started', 'Started'),
            ('blocked', 'Blocked'),
            ('paused', 'Paused'),
            ('done', 'Done')
        ], string='Tracking Status', default="draft"
    )

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        default['fal_tracking_state'] = 'draft'
        return super(MrpProduction, self).copy_data(default)

    @api.multi
    def time_start(self):
        for mrp in self:
            mrp.workorder_ids.with_context(fal_type='routing').button_start()
            start = datetime.now()
            if mrp.fal_tracking_ids:
                last = mrp.fal_tracking_ids.sorted(
                    key=lambda r: r.id, reverse=True)
                if last:
                    start = last[0].end_hour
            self.env['fal.mrp.production.tracking'].create({
                'start_hour': start,
                'name': _('Time Tracking: ') + self.env.user.name,
                'mrp_id': mrp.id,
                'uom_id': mrp.product_uom_id.id,
                'tracking_ids': [(6, 0, mrp.fal_tracking_ids.ids)]
            })
            mrp.write({'fal_tracking_state': 'started'})
        return True

    @api.multi
    def time_stop(self):
        for mrp in self:
            for wo in mrp.workorder_ids:
                wo.record_production()
            last = mrp.fal_tracking_ids.filtered(lambda r: not r.end_hour)
            last.sorted(key=lambda r: r.id, reverse=True)
            if last:
                last[0].write({'end_hour': datetime.now()})
            mrp.write({'fal_tracking_state': 'done'})
        return True

    @api.multi
    def time_pause(self):
        for mrp in self:
            mrp.workorder_ids.button_pending()
            last = mrp.fal_tracking_ids.filtered(lambda r: not r.end_hour)
            last.sorted(key=lambda r: r.id, reverse=True)
            if last:
                last[0].write({'end_hour': datetime.now()})
            mrp.write({'fal_tracking_state': 'paused'})
        return True

    @api.multi
    def time_block(self):
        for item in self:
            working = item.workorder_ids.mapped('fal_wokrshop_id')
            wiz = self.env['fal.block.wizard'].create({
                'workshop_ids': [(6, 0, working.ids)]
            })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.block.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wiz.id,
        }

    @api.multi
    def time_unblock(self):
        for mrp in self:
            mrp.write({'fal_tracking_state': 'started'})
        return True


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    fal_tracking_type = fields.Selection(
        related='production_id.fal_tracking_type',
        string='Time Tracking Type',
    )

    @api.multi
    def button_start(self):
        ctx = dict(self._context)
        if ctx.get('fal_type', False) == 'routing':
            return self.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })
        return super(MrpWorkOrder, self).button_start()

    @api.multi
    def end_all(self):
        for item in self:
            if item.fal_tracking_type != 'workorder':
                return True
        return super(MrpWorkOrder, self).end_all()

    @api.multi
    def end_previous(self, doall=False):
        for item in self:
            if item.fal_tracking_type != 'workorder':
                return True
        return super(MrpWorkOrder, self).end_previous(doall)

    def _compute_is_user_working(self):
        res = super(MrpWorkOrder, self)._compute_is_user_working()
        for order in self:
            if order.fal_tracking_type != 'workorder':
                order.is_user_working = True
        return res


class FalMrpProductionTracking(models.Model):
    _name = 'fal.mrp.production.tracking'
    _description = 'Production Tracking'

    name = fields.Char(string='Name')
    qty = fields.Float(string='Produced Qty')
    remain_qty = fields.Float(string='Remaining Qty', compute='get_remain')
    uom_id = fields.Many2one('uom.uom', string='UoM')
    cycle_time = fields.Float(string='Cycle Time', compute='get_cycle_time')
    start_hour = fields.Datetime(string='Departure Hour')
    end_hour = fields.Datetime(string='Ending Hour')
    mrp_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    tracking_ids = fields.Many2many(
        'fal.mrp.production.tracking', 'remain_qty_fal_rel',
        'tracking_id1', 'tracking_id2', string='Previous Tracking'
    )
    loss_id = fields.Many2one(
        'mrp.workcenter.productivity.loss', "Loss Reason",
        ondelete='restrict')
    loss_type = fields.Selection(
        "Effectiveness", related='loss_id.loss_type', store=True)
    fal_workshop_id = fields.Many2one(
        'mrp.workcenter', string='Working Machine'
    )
    notes = fields.Text(string="Notes")

    @api.depends(
        'mrp_id', 'mrp_id.bom_id', 'mrp_id.bom_id.product_qty',
        'start_hour', 'end_hour', 'qty'
    )
    def get_cycle_time(self):
        for item in self:
            if item.end_hour and item.start_hour and item.mrp_id and \
                    item.mrp_id.bom_id and item.mrp_id.bom_id.product_qty:
                diff = fields.Datetime.from_string(item.end_hour) - \
                    fields.Datetime.from_string(item.start_hour)
                item.cycle_time = item.qty / float(diff.seconds) /\
                    item.mrp_id.bom_id.product_qty * 3600.0
            else:
                item.cycle_time = 0.0

    @api.depends(
        'mrp_id', 'mrp_id.product_qty')
    def get_remain(self):
        for item in self:
            before = item.mrp_id.fal_tracking_ids.filtered(
                lambda r: r.id < item.id)
            prod_qty = sum(before.mapped('qty'))
            item.remain_qty = item.mrp_id.product_qty - prod_qty - item.qty


class MrpWorkcenterProductivityLoss(models.Model):
    _inherit = "mrp.workcenter.productivity.loss"

    fal_working_machine = fields.Boolean(string="Using Working Machine")
