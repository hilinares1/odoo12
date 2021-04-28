# -*- coding: utf-8 -*-
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp
from odoo.tools import float_round
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    @api.multi
    def action_report_mrp_bom(self):
        templates = self.filtered(lambda t: t.product_variant_count == 1 and t.bom_count > 0)
        if templates:
            return templates.mapped('product_variant_id').action_report_mrp_bom()

    @api.multi
    def action_set_cost_from_bom(self):
        if hasattr(self, 'property_cost_method') and any(tmpl.property_cost_method != 'standard' for tmpl in self):
            raise UserError(_("Some product not supported for manual update cost price"))
        
        for tmpl in self:
            # if tmpl has unique variant, apply to the variant
            if len(tmpl.product_variant_ids) == 1:
                bom_cost = self.get_cost(tmpl)
                tmpl.product_variant_ids.write({
                    'standard_price': bom_cost
                    })
                tmpl._set_standard_price()

    @api.model
    def _get_bom(self, product_id):
        # only return One BOM
        return product_id.bom_ids and product_id.bom_ids[0]

    @api.model
    def get_cost(self, product_id):
        cost_of_bom = 0.00
        uom_obj = self.env['uom.uom']
        bom_id = self._get_bom(product_id)
        if bom_id:
            for bom_line in bom_id[0].bom_line_ids:
                pro_qty = bom_line.product_qty
                if bom_line.product_uom_id.id != bom_line.product_uom_id.id:
                    pro_qty = uom_obj._compute_qty(
                        bom_line.product_uom_id.id,
                        bom_line.product_qty,
                        bom_line.product_uom_id.id
                    )
                if bom_line.product_id.bom_ids:
                    cost_of_bom += pro_qty * self.get_cost(bom_line.product_id)
                else:
                    cost_of_bom += pro_qty * bom_line.product_id.standard_price
        else:
            cost_of_bom = product_id.standard_price
        return cost_of_bom

    @api.multi
    @api.depends('bom_ids')
    def _get_cost_bom(self):
        for prod_tmpl in self:
            cost_of_bom = 0.0
            bom = self.env['mrp.bom']._bom_find(product=prod_tmpl.product_variant_id)
            if bom:
                cost_of_bom = prod_tmpl.product_variant_id._get_price_from_bom()
            bom_id = self._get_bom(prod_tmpl)

            prod_tmpl.fal_bom_costs = cost_of_bom
            prod_tmpl.fal_bom_cost_scrap = bom_id.fal_scrap_percentage/100 * cost_of_bom
    
    @api.multi
    @api.depends('standard_price', 'list_price')
    def _compute_cost_sale_price_margin(self):
        for prod_tmpl in self:
            prod_tmpl.fal_margin_cost_sale_price = prod_tmpl.list_price - prod_tmpl.standard_price
    
    @api.multi
    @api.depends('fal_bom_costs', 'list_price')
    def _compute_bom_cost_sale_price_margin(self):
        for prod_tmpl in self:
            prod_tmpl.fal_margin_bom_sale_price = prod_tmpl.list_price - prod_tmpl.fal_bom_costs

    @api.multi
    @api.depends('bom_ids')
    def _compute_operation_cost(self):
        for prod_tmpl in self:
            bom_id = self._get_bom(prod_tmpl)
            routing_id = bom_id.routing_id
            total = 0.0
            for operation in routing_id.operation_ids:
                operation_cycle = float_round(1 / operation.workcenter_id.capacity, precision_rounding=1, rounding_method='UP')
                duration_expected = operation_cycle * operation.time_cycle + operation.workcenter_id.time_stop + operation.workcenter_id.time_start
                total += ((duration_expected / 60.0) * operation.workcenter_id.costs_hour)
            prod_tmpl.fal_operation_cost = total

    @api.multi
    @api.depends('fal_operation_cost', 'fal_bom_costs')
    def _compute_bom_operation_cost(self):
        for prod_tmpl in self:
            prod_tmpl.fal_bom_operation_cost = prod_tmpl.fal_operation_cost + prod_tmpl.fal_bom_costs


    fal_bom_costs = fields.Float(
        compute='_get_cost_bom',
        string='Cost of BoM',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user",
        help = "Cost based on BOM used for information."
    )

    fal_bom_cost_scrap = fields.Float(
        compute='_get_cost_bom',
        string='Cost of Scrap',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user",
        help = "Cost of BOM Scrap."
    )

    fal_operation_cost = fields.Float(
        compute='_compute_operation_cost',
        string='Operation Cost',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user"
    )

    fal_bom_operation_cost = fields.Float(
        compute='_compute_bom_operation_cost',
        string='Cost of BoM + Operation Cost',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user",
        help = "Cost of BoM + Operation Cost."
    )

    fal_margin_cost_sale_price = fields.Float(
        compute='_compute_cost_sale_price_margin',
        string='Margin of Cost & Sale Price',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user",
        help = "Margin of Cost & Sale Price."
    )

    fal_margin_bom_sale_price = fields.Float(
        compute='_compute_bom_cost_sale_price_margin',
        string='Margin of Cost of Bom & Sale Price',
        digits=dp.get_precision('BoM Cost'), groups="base.group_user",
        help = "Margin of Cost of Bom & Sale Price."
    )


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    _description = 'Product'

    @api.multi
    def action_report_mrp_bom(self):
        self.ensure_one()
        bom = self.env['mrp.bom']._bom_find(product=self)
        if bom:
            action = self.env.ref('mrp.action_report_mrp_bom')
            context = {
                'model': 'report.mrp.report_bom_structure',
                'active_id': bom.id
                }
            res = {
                'type': 'ir.actions.client',
                'name': action.name,
                'tag': action.tag,
                'context': context
            }
            return res
