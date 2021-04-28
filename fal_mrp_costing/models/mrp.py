from odoo import models, fields, api


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    fal_hourly_cost_ids = fields.Many2many(
        'fal.hourly.cost', string='Hourly Costs')
    fal_hourly_cost_id = fields.Many2one(
        'fal.hourly.cost', string='Default Hourly Cost', readonly=True)

    @api.onchange('fal_hourly_cost_ids')
    def onchange_hourly_cost(self):
        cost_type = self.fal_hourly_cost_id.search(
            [
                ('default', '=', True),
                ('id', 'in', self.fal_hourly_cost_ids.ids)], limit=1)
        if self.fal_hourly_cost_ids:
            self.fal_hourly_cost_id = cost_type.id


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    fal_hourly_cost_ids = fields.Many2many(
        'fal.hourly.cost', string='Hourly Cost',
        related='workcenter_id.fal_hourly_cost_ids')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    fal_mrp_cost_preview_ids = fields.One2many(
        'fal.mrp.cost.preview',
        'bom_id', string='Cost Preview')

    @api.multi
    def action_refresh(self):
        cost_preview = self.env['fal.mrp.cost.preview']
        _type = []
        res = {}
        for item in self:
            if item.fal_mrp_cost_preview_ids:
                item.fal_mrp_cost_preview_ids.unlink()
            operation = item.routing_id.operation_ids
            for cost_type in operation:
                for cost in cost_type.fal_hourly_cost_ids:
                    total_cost = (cost.amount_total / 60) \
                        * cost_type.time_cycle_manual
                    _type.append((cost.name, total_cost))
        for amount, val in _type:
            if amount in res:
                res[amount] += val
            else:
                res[amount] = val
        # end get cost of bom
        for key in res:
            vals = {
                'hourly_cost': res[key],
                'bom_id': item.id,
                'name': key,
            }
            cost_preview.create(vals)
