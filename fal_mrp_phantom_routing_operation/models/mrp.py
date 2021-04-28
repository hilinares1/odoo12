from odoo import api, models, fields, _
import math
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError, ValidationError


class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    fal_is_phantom = fields.Boolean(string='No Work Order')


class MrpRouting(models.Model):
    _inherit = 'mrp.routing'

    @api.multi
    @api.constrains('operation_ids')
    def _check_reconcile(self):
        for routing in self:
            # 1st Check if there is routing operation ids
            if routing.operation_ids:
                # 2nd check if any of it have the operation ids that "No work order" button is unchecked
                have_no_phantom = False
                for operation in routing.operation_ids:
                    if operation.fal_is_phantom == False:
                        have_no_phantom = True
                if not have_no_phantom:
                    raise ValidationError(_('Need at least 1 Work Center Operation with Work Order'))


class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    def _workorders_create(self, bom, bom_data):
        """
        :Need to override this method, so that it doesn't create workorder for phantom Routing Workcenter
        """
        workorders = self.env['mrp.workorder']
        bom_qty = bom_data['qty']

        # Initial qty producing
        if self.product_id.tracking == 'serial':
            quantity = 1.0
        else:
            quantity = self.product_qty - sum(self.move_finished_ids.mapped('quantity_done'))
            quantity = quantity if (quantity > 0) else 0

        # Filter Operation that is Phantom
        for operation in bom.routing_id.operation_ids.filtered(lambda o: o.fal_is_phantom == False):
            # create workorder
            cycle_number = float_round(bom_qty / operation.workcenter_id.capacity, precision_digits=0, rounding_method='UP')
            duration_expected = (operation.workcenter_id.time_start +
                                 operation.workcenter_id.time_stop +
                                 cycle_number * operation.time_cycle * 100.0 / operation.workcenter_id.time_efficiency)
            workorder = workorders.create({
                'name': operation.name,
                'production_id': self.id,
                'workcenter_id': operation.workcenter_id.id,
                'operation_id': operation.id,
                'duration_expected': duration_expected,
                'state': len(workorders) == 0 and 'ready' or 'pending',
                'qty_producing': quantity,
                'capacity': operation.workcenter_id.capacity,
            })
            if workorders:
                workorders[-1].next_work_order_id = workorder.id
            workorders += workorder

            # assign moves; last operation receive all unassigned moves (which case ?)
            moves_raw = self.move_raw_ids.filtered(lambda move: move.operation_id == operation)
            if len(workorders) == len(bom.routing_id.operation_ids):
                moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
            moves_finished = self.move_finished_ids.filtered(lambda move: move.operation_id == operation) #TODO: code does nothing, unless maybe by_products?
            moves_raw.mapped('move_line_ids').write({'workorder_id': workorder.id})
            (moves_finished + moves_raw).write({'workorder_id': workorder.id})

            workorder._generate_lot_ids()
        return workorders
