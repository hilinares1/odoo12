# -*- coding: utf-8 -*-
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    fal_of_number = fields.Char(
        'PO Number',
        size=64,
        help="Sequence for Finished Product",
        copy=False,
        compute='_get_production_number',
        store=True
    )
    fal_parent_mo_id = fields.Many2one('mrp.production', 'Parent MO')
    fal_mo_line_ids = fields.One2many(
        'mrp.production',
        'fal_parent_mo_id',
        'Manufacture Order Lines', copy=False
    )

    @api.depends('fal_prod_order_id')
    def _get_production_number(self):
        for mrp in self:
            mrp.fal_of_number = mrp.fal_prod_order_id.name

    # not use this, we chnage to compute method
    # @api.model
    # def fal_get_finished_product_number(self, production):
    #     finished_product_number = False
    #     if not production.fal_of_number:
    #         finished_product_number =\
    #             self.env['ir.sequence'].next_by_code(
    #                 'finished.product.fwa') or '/'
    #     return finished_product_number

    # @api.multi
    # def _generate_moves(self):
    #     for production in self:
    #         finished_product_number =\
    #             production.fal_get_finished_product_number(production)
    #         if finished_product_number:
    #             production.write({
    #                 'fal_of_number': finished_product_number
    #             })
    #     return super(mrp_production, self)._generate_moves()

    def _generate_finished_moves(self):
        move = super(
            mrp_production, self)._generate_finished_moves()
        move.write({'fal_of_number': self.fal_of_number})
        return move

    def _generate_raw_move(self, bom_line, line_data):
        res = super(
            mrp_production, self)._generate_raw_move(bom_line, line_data)
        res.write({'fal_of_number': self.fal_of_number})
        return res


class stock_move(models.Model):
    _inherit = 'stock.move'

    fal_of_number = fields.Char(
        string="PO Number",
        size=128,
        compute='_get_production_number',
    )

    def _prepare_procurement_values(self):
        res = super(stock_move, self)._prepare_procurement_values()
        res['fal_of_number'] = self.raw_material_production_id.fal_of_number
        res['fal_parent_mo_id'] = self.raw_material_production_id.id
        return res

    def _get_production_number(self):
        for stock in self:
            po_number = False
            if stock.sale_line_id and stock.sale_line_id.fal_production_order_id:
                po_number = stock.sale_line_id.fal_production_order_id.name
            else:
                mrp = self.env['mrp.production'].search([('name', '=', stock.origin)])
                if mrp:
                    po_number = mrp.fal_prod_order_id.name
            stock.fal_of_number = po_number


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    fal_of_number = fields.Char(
        string='PO Number',
        size=64,
        help="Sequence for Finished Product"
    )
    fal_parent_mo_id = fields.Many2one(
        'mrp.production',
        'Parent Manufacturing Order'
    )


class product_category(models.Model):
    _inherit = "product.category"

    isfal_finished_product = fields.Boolean('Finished Product')
    isfal_parts_product = fields.Boolean('Parts Product')


class stock_rule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, values, bom):
        res = super(stock_rule, self)._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom)
        res['fal_of_number'] = values.get('fal_of_number')
        res['fal_parent_mo_id'] = values.get('fal_parent_mo_id')
        return res


class FalProductionOrder(models.Model):
    _inherit = 'fal.production.order'

    # def _prepare_mo_vals(self, bom):
    #     res = super(FalProductionOrder, self)._prepare_mo_vals(bom)
    #     res['fal_of_number'] = self.name
    #     return res

    @api.multi
    def fal_get_finished_product_number(
            self, product_id, sale_order_line_id=False):
        """
            to devine sequence of PO Number in production.order
        """
        finished_product_number = False
        if sale_order_line_id:
            # means it is finished product, so we use this sequence
            finished_product_number = self.env['ir.sequence'].\
                next_by_code('finished.product.fwa') or '/'
        else:
            # directly create in production.order
            # sequence is different according to the product
            if product_id.categ_id.isfal_parts_product:
                finished_product_number = self.env['ir.sequence'].\
                    next_by_code('parts.product.fwa') or '/'
        if not finished_product_number:
            # directly create in production.order
            if product_id.categ_id.isfal_finished_product:
                # if product category is finished product
                finished_product_number = self.env['ir.sequence'].next_by_code(
                    'finished.product.fwa') or '/'
        return finished_product_number

    @api.model
    def create(self, vals):
        """
            by using fal_get_finished_product_number() we got next_by_code
            to generate next sequence by duplicating production.order
        """
        if vals['product_id']:
            sol_id = False
            if 'fal_sale_order_line_id' in vals:
                sol_id = vals['fal_sale_order_line_id']
            finished_product_number = self.fal_get_finished_product_number(
                self.env['product.product'].browse(vals['product_id']),
                sol_id
            )
            # after using fal_get_finished_product_number() we got C183089
            if finished_product_number:
                # put C183089 in the new duplicated record
                vals["name"] = finished_product_number
        return super(FalProductionOrder, self).create(vals)
