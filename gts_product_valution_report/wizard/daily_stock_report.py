from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.float_utils import float_is_zero

import time
import logging
_logger = logging.getLogger('Stock Report')
from datetime import datetime, timedelta
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
try:
    import xlwt
    import xlsxwriter
    from xlwt.Utils import rowcol_to_cell
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')
import base64
import os
import tempfile


class daily_stock_report(models.TransientModel):
    _name = "daily.stock.report"

    name = fields.Char('File Name', readonly=True)
    from_date = fields.Date('Start Date')
    to_date = fields.Date('End Date', default=time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.user.company_id.id)
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_rel_report_wiz', 'wiz_id',
                                     'warehouse_id', 'Warehouses')
    location_ids = fields.Many2many('stock.location', 'location_rel_report_wiz', 'wiz_id',
                                    'location_id', 'Locations')
    product_ids = fields.Many2many('product.product', 'product_rel_report_wiz', 'wiz_id',
                                   'product_id', 'Products')
    show_valuation = fields.Boolean('Valuation', default=True,
                                    help='Show valuation of stock?')
    skip_zero_stock = fields.Boolean('Skip Zero Stock?', default=False,
                                    help='Skip locations / products who has 0 stock?')
    all_locations = fields.Boolean('All Locations?', default=False, help='Select to ')
    report_by = fields.Selection([('all', 'Summarised Report'),
                                  ('location_wise', 'Location Wise Report')], default='location_wise',
                                 help='Select location wise if report is required location wise.')
    product_value_ids = fields.Many2many('product.attribute.value', 'attribute_id', 'name',
                                         string='Product Attribute Value', help='Select Attribute value to filter')

    @api.multi
    def get_locations(self):
        location_obj = self.env['stock.location']
        locations = location_obj
        if self.warehouse_ids:
            for w in self.warehouse_ids:
                if w.lot_stock_id.usage == 'internal':
                    locations += w.lot_stock_id
                location_recs = location_obj.search([('location_id.name', '=', w.code)])
                locations += location_recs
        else:
            if self.location_ids:
                locations += self.location_ids
            else:
                locations += location_obj.search([
                    ('usage', '=', 'internal'), '|', ('company_id', '=', self.company_id.id),
                    ('company_id', '=', False)], order='level asc')
        return locations

    @api.multi
    def get_child_locations(self, location):
        location_obj = self.env['stock.location']
        child_list = iteration_list = location.ids
        while iteration_list:
            for loc in location_obj.browse(iteration_list):
                if loc.child_ids.filtered(lambda l: l.usage == 'internal'):
                    child_list += loc.child_ids.filtered(lambda l: l.usage == 'internal').ids
                    iteration_list += loc.child_ids.filtered(lambda l: l.usage == 'internal').ids
                iteration_list = list(set(iteration_list))
                if loc.id in iteration_list:
                    iteration_list.remove(loc.id)
        if child_list:
            child_list = list(set(child_list))
        return child_list and location_obj.browse(child_list) or location

    @api.multi
    def get_product_available(self, product, from_date=False, to_date=False, location=False,
                              warehouse=False, compute_child=True):
        """ Function to return stock """
        locations = self.get_child_locations(location)
        date_str, date_values = False, False
        where = [tuple(locations.ids), tuple(locations.ids), tuple([product.id])]
        if from_date and to_date:
            date_str = "move.date::DATE>=%s and move.date::DATE<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "move.date::DATE>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "move.date::DATE<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'incoming'
            group by product_id, product_uom''', tuple(where))
        results_incoming = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'outgoing'
            group by product_id, product_uom''', tuple(where))
        results_outgoing = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'internal'
            group by product_id, product_uom''', tuple(where))
        results_internal_in = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            INNER JOIN stock_picking picking ON (move.picking_id = picking.id)
            INNER JOIN stock_picking_type picking_type ON (picking.picking_type_id = picking_type.id)
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is not null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' and picking_type.code = 'internal'
            group by product_id, product_uom''', tuple(where))
        results_internal_out = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is not null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            '''
            group by product_id, product_uom''', tuple(where))
        results_adjustment_in = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is not null
            '''  + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' group by product_id, product_uom''', tuple(where))
        results_adjustment_out = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            where move.location_id NOT IN %s
            and move.location_dest_id IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is null
            '''
            + (date_str and 'and ' + date_str + ' ' or '') + \
            '''
            group by product_id, product_uom''', tuple(where))
        results_production_in = self._cr.fetchall()

        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom, COALESCE(sum(product_uom_qty * price_unit), 0)
            from stock_move move 
            where move.location_id IN %s
            and move.location_dest_id NOT IN %s
            and product_id IN %s and move.state = 'done' 
            and move.picking_id is null
            and move.inventory_id is null
            ''' + (date_str and 'and ' + date_str + ' ' or '') + \
            ''' group by product_id, product_uom''', tuple(where))
        results_production_out = self._cr.fetchall()

        incoming, outgoing, internal, adjustment, production = 0, 0, 0, 0, 0
        incoming_val, outgoing_val, internal_val, adjustment_val, production_val = 0, 0, 0, 0, 0
        # Count the quantities
        for quantity, prod_id, prod_uom, val in results_incoming:
            incoming += quantity
            incoming_val += val
        for quantity, prod_id, prod_uom, val in results_outgoing:
            outgoing += quantity
            outgoing_val += val
        for quantity, prod_id, prod_uom, val in results_internal_in:
            internal += quantity
            internal_val += val
        for quantity, prod_id, prod_uom, val in results_internal_out:
            internal -= quantity
            internal_val -= val
        for quantity, prod_id, prod_uom, val in results_adjustment_in:
            adjustment += quantity
            adjustment_val += val
        for quantity, prod_id, prod_uom, val in results_adjustment_out:
            adjustment -= quantity
            adjustment_val -= val
        for quantity, prod_id, prod_uom, val in results_production_in:
            production += quantity
            production_val += val
        for quantity, prod_id, prod_uom, val in results_production_out:
            production -= quantity
            production_val -= val
        return {
            'incoming': incoming,
            'outgoing': outgoing,
            'internal': internal,
            'adjustment': adjustment,
            'production': production,
            'balance': incoming - outgoing + internal + adjustment + production,
            'balance_val': incoming_val - outgoing_val + internal_val + adjustment_val + production_val,
            'incoming_val': incoming_val,
            'outgoing_val': outgoing_val,
            'internal_val': internal_val,
            'adjustment_val': adjustment_val,
            'production_val': production_val,
        }

    @api.multi
    def act_getstockreport(self):
        self._cr.execute('''delete from product_valution_data''')
        product_obj = self.env['product.product']
        price_prec = self.env['decimal.precision'].precision_get('Product Price')
        # Getting locations to fetch report for
        locations = self.get_locations()
        locations = self.env['stock.location'].browse(list(set(locations.ids)))
        locations = locations.sorted(lambda l: l.level)
        products = self.product_ids
        # products = product_obj.browse(41)
        if not products:
            if self.product_value_ids:
                products = product_obj.search([('attribute_value_ids', 'in', self.product_value_ids.ids)])
            else:
                products = product_obj.search([])

        warehouse_name = ''
        if self.warehouse_ids:
            for w in self.warehouse_ids:
                warehouse_name = warehouse_name + w.name + ', '
        else:
            warehouse_name = 'ALL'

        if self.from_date:
            previous_date = datetime.strftime((datetime.strptime(
                str(self.from_date), DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=1)),
                                              DEFAULT_SERVER_DATE_FORMAT)
        for product in products.sorted(lambda p: p.name):
            processed_loc_ids = []
            attribute_name = ''
            for value in product.attribute_value_ids:
                attribute_name = attribute_name + value.name + ', '
            # if self.report_by == 'location_wise':
            for location in locations:
                if location.id in processed_loc_ids:
                    continue
                child_locations = self.get_child_locations(location)
                processed_loc_ids += child_locations.ids
                col = 0
                opening_dict = {}
                if self.from_date:
                    opening_dict = self.get_product_available(product, False, previous_date,
                                                              location)
                inventory_dict = self.get_product_available(product, self.from_date, self.to_date,
                                                            location)
                closing_balance = opening_dict.get('balance', 0.0) + inventory_dict.get('balance', 0.0)
                closing_balance_val = opening_dict.get('balance_val', 0.0) + inventory_dict.get('balance_val', 0.0)
                if self.skip_zero_stock and \
                        float_is_zero(closing_balance, precision_digits=price_prec):
                    continue

                dic = {
                    'internal_reference': product.default_code,
                    'product_name': product.name,
                    'cost': product.standard_price,
                    'stock_before_adjust': opening_dict.get('balance', 0.0),
                    'adjustment_stock': inventory_dict.get('adjustment', 0.0),
                    'location_id': location.id,
                    'incoming': inventory_dict.get('incoming', 0.0),
                    'outgoing': inventory_dict.get('outgoing', 0.0),
                    'internal': inventory_dict.get('internal', 0.0),
                    'diffrence_stock': inventory_dict.get('adjustment', 0.0)-opening_dict.get('balance', 0.0),
                    'valution_difference_qty': (inventory_dict.get('adjustment', 0.0)-opening_dict.get('balance', 0.0))*product.standard_price
                }
                self.env['product.valution.data'].create(dic)
        action = {
            'type': 'ir.actions.act_window',
            # 'views': [
            #     (tree_view_id, 'tree'), (form_view_id, 'form'),
            #     (graph_view_id, 'graph'), (pivot_view_id, 'pivot')
            # ],
            'view_type': 'form',
            'view_mode': 'pivot',
            'name': _('Stock Report'),
            'res_model': 'product.valution.data',
            # 'search_view_id': search_view_ref and search_view_ref.id,
        }
        return action


class Productvalution(models.Model):
    _name = 'product.valution.data'

    internal_reference = fields.Char("Internal Reference")
    product_name = fields.Char("Product Name")
    cost = fields.Float('Cost')
    stock_before_adjust = fields.Float("Stock Before Adjustment")
    adjustment_stock = fields.Float("Adjustment Stock")
    diffrence_stock = fields.Float("Difference Quantity")
    valution_difference_qty = fields.Float("Valution Difference Quantity")
    location_id = fields.Many2one('stock.location', "Location")
    incoming = fields.Float("Incoming")
    outgoing = fields.Float("Outgoing")
    internal = fields.Float("Internal")
