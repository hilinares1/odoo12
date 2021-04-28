# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class FalRoutingExt(models.TransientModel):
    _name = "fal.routing.ext"
    _description = "Routing Wizard"

    @api.model
    def _get_default_workorder_ids(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        workorder_ids = self.env['mrp.workorder'].search([
            ('production_id', '=', active_id)]).ids
        return [(6, 0, workorder_ids)]

    @api.model
    def _get_default_move_line(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        workorder_ids = self.env['mrp.workorder'].search([
            ('production_id', '=', active_id)])
        move_lines = []
        for wo in workorder_ids:
            move_lines += wo.active_move_line_ids.ids
        return move_lines

    workorder_ids = fields.Many2many('mrp.workorder', string = 'Work Orders', default=_get_default_workorder_ids)
    is_product_tracked = fields.Boolean('Product is tracked', compute='_compute_product_tracked')
    product_id = fields.Many2one('product.product', 'Product', compute='_compute_product_selected')
    next_wo_id = fields.Many2one(
        'mrp.workorder',
        string="Next Work Order to Use",
        compute="_compute_next_wo")
    final_lot_id = fields.Many2one(
        'stock.production.lot',
        string='Lot/Serial Number')
    active_move_line_ids = fields.Many2many('stock.move.line', string="BOM", default=_get_default_move_line)
    date_end = fields.Datetime('End Date', required=True)

    @api.depends('workorder_ids')
    def _compute_next_wo(self):
        for item in self.workorder_ids:
            self.next_wo_id = item.id

    @api.depends('workorder_ids')
    def _compute_product_selected(self):
        for item in self.workorder_ids:
            self.product_id = item.product_id.id

    @api.depends('workorder_ids')
    def _compute_product_tracked(self):
        for item in self.workorder_ids:
            if item.production_id.product_id.tracking != 'none':
                self.is_product_tracked = True
            else:
                self.is_product_tracked = False

    def button_finish_mo(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        mrp_production = self.env['mrp.production'].browse(active_id)
        if mrp_production.workorder_ids:
            for workorder in mrp_production.workorder_ids:
                workorder.final_lot_id = self.final_lot_id.id
                for quality_check in workorder.check_ids:
                    quality_check.do_pass()
                workorder.button_start()
                workorder.do_finish()
                for time_id in workorder.time_ids:
                    time_id.date_end = self.date_end
        mrp_production.button_mark_done()
