# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    @api.one
    @api.depends('move_raw_ids')
    def _fal_moves_check_stock(self):
        is_ready = True
        for move_line in self.move_raw_ids:
            if move_line.state != 'assigned':
                if move_line.product_qty > move_line.reserved_availability:
                    is_ready = False
        self.fal_component_ready = is_ready

    # field start here
    # i dont think this state is used on this module.
    # need functional confirmation
    # state = fields.Selection(
    #     selection_add=[
    #         ('Component Ready', 'Awaiting Reserved'),
    #     ]
    # )
    fal_floating_production_date = fields.Date(
        "Floating Production Date",
        readonly=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]},
        copy=False
    )
    fal_fixed_production_date = fields.Date(
        "Fixed Production Date",
        readonly=True,
        states={'draft': [('readonly', False)], 'confirmed': [('readonly', False)]},
        copy=False
    )
    fal_component_ready = fields.Boolean(
        compute='_fal_moves_check_stock',
        string='Component Ready'
    )

    @api.multi
    def action_assign(self):
        res = super(mrp_production, self).action_assign()
        for production in self:
            if production.fal_prod_order_id and production.fal_prod_order_id.is_ready and production.fal_prod_order_id.state == 'confirm':
                production.fal_prod_order_id.write({'state': 'ready'})
        return res

    @api.multi
    def _production_fixed(self):
        for mrp_id in self:
            if mrp_id.fal_floating_production_date:
                mrp_id.write({'fal_fixed_production_date': mrp_id.fal_floating_production_date})
            else:
                mrp_id.write({'fal_fixed_production_date': fields.Date.today()})
        return True

    @api.multi
    def write(self, vals):
        res = super(mrp_production, self).write(vals)
        for mrp_id in self:
            if vals.get('fal_floating_production_date', False):
                if mrp_id.fal_fixed_production_date:
                    raise UserError(_('MO %s is already fixed, cannot be change !') % (mrp_id.name))
        return res

    @api.model
    def create(self, vals):
        product_obj = self.env['product.product']
        if not vals.get('fal_floating_production_date', False):
            product_id = product_obj.browse(vals['product_id'])
            if product_id.categ_id.isfal_finished_product:
                vals['fal_floating_production_date'] = vals.get('date_planned_start', False)
        return super(mrp_production, self).create(vals)


class mrp_production_workcenter_line(models.Model):
    _inherit = 'mrp.workorder'

    allday = fields.Boolean('Allday', default=1)
    date_planned = fields.Datetime(
        'Scheduled Date',
        readonly=True,
        states={'draft': [('readonly', False)]})
    date_start = fields.Datetime(
        'Start Date',
        readonly=True,
        states={'draft': [('readonly', False)]})
