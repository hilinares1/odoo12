from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF
from odoo.exceptions import UserError


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _run_manufacture(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        Production = self.env['mrp.production']
        ProductionSudo = Production.sudo().with_context(force_company=values['company_id'].id)
        bom = self._get_matching_bom(product_id, values)
        if not bom:
            msg = _('There is no Bill of Material found for the product %s. Please define a Bill of Material for this product.') % (product_id.display_name,)
            raise UserError(msg)

        # create the MO as SUPERUSER because the current user may not have the rights to do it (mto product launched by a sale for example)
        production = ProductionSudo.create(self._prepare_mo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom))
        origin_production = values.get('move_dest_ids') and values['move_dest_ids'][0].raw_material_production_id or False
        orderpoint = values.get('orderpoint_id')
        if orderpoint:
            production.message_post_with_view('mail.message_origin_link',
                                              values={'self': production, 'origin': orderpoint},
                                              subtype_id=self.env.ref('mail.mt_note').id)
        if origin_production:
            production.message_post_with_view('mail.message_origin_link',
                                              values={'self': production, 'origin': origin_production},
                                              subtype_id=self.env.ref('mail.mt_note').id)

        # If the origin of this manufacture order are from Manufacture
        # Means that this Manufacture order are child manufacture order, so assign it's origin as parent
        parent_mo_id = ProductionSudo.search([('name', '=', production.origin)], limit=1)
        if parent_mo_id:
            production.parent_id = parent_mo_id.id

        # If Mo are top parent MO and no production order yet, create one
        if not production.parent_id and not production.fal_prod_order_id:
            MPO = self.env['fal.production.order']
            bom = self._get_matching_bom(product_id, values)
            mpo_val = self._prepare_fal_mpo_vals(product_id, product_qty, product_uom, location_id, name, origin, values, bom)
            production_id = MPO.create(mpo_val)
            production.fal_prod_order_id = production_id.id

        return True

    def _prepare_fal_mpo_vals(
        self, product_id, product_qty, product_uom,
        location_id, name, origin, values,
        bom
    ):
        date_planned_start = values.get('date_planned')
        company_id = values.get('company_id')
        first_day = date_planned_start - \
            timedelta(date_planned_start.weekday())
        location_src = self.picking_type_id.default_location_src_id.id
        location_dest = self.picking_type_id.default_location_dest_id.id
        picking_type_id = self.picking_type_id.id or \
            self.warehouse_id.manu_type_id.id
        if not bom:
            raise UserError(_(
               'There is no Bill of Material found for the product %s. Please define a Bill of Material for this product.') % (product_id.display_name))
        return {
            'delivery_planned_date': date_planned_start,
            'production_date_planned': first_day,
            'origin': origin,
            'product_id': product_id.id,
            'qty_to_produce': product_qty,
            'product_uom_id': product_uom.id,
            'location_src_id': location_src,
            'location_dest_id': location_dest,
            'bom_id': bom.id,
            'propagate': self.propagate,
            'picking_type_id': picking_type_id,
            'company_id': company_id.id,
            'procurement_group_id': values.get('group_id').id if values.get('group_id', False) else False,
            'move_dest_ids': values.get(
                'move_dest_ids'
            ) and [(4, x.id) for x in values['move_dest_ids']] or False,
        }
