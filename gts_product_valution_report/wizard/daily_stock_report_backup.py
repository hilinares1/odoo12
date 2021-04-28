from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

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


class daily_stock_report(models.TransientModel):
    _name = "daily.stock.report"

    name = fields.Char('File Name', readonly=True)
    from_date = fields.Date('Start Date')
    to_date = fields.Date('End Date', default=time.strftime('%Y-%m-%d'))
    company_id = fields.Many2one('res.company', 'Company')
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_rel_report_wiz', 'wiz_id',
                                     'warehouse_id', 'Warehouses')
    location_ids = fields.Many2many('stock.location', 'location_rel_report_wiz', 'wiz_id',
                                    'location_id', 'Locations')
    product_ids = fields.Many2many('product.product', 'product_rel_report_wiz', 'wiz_id',
                                   'product_id', 'Products')
    show_valuation = fields.Boolean('Valuation', default=False,
                                    help='Show valuation of stock?')

    @api.multi
    def get_locations(self):
        location_obj = self.env['stock.location']
        warehouse_obj = self.env['stock.warehouse']
        locations = location_obj
        if self.warehouse_ids:
            for w in self.warehouse_ids:
                locations += w.lot_stock_id
        if self.location_ids:
            locations += self.location_ids
        elif not self.warehouse_ids:
            warehouses = warehouse_obj.search([])
            for w in warehouses:
                locations += w.lot_stock_id
        return locations

    @api.multi
    def get_child_locations(self, location):
        location_obj = self.env['stock.location']
        locations = location
        # child_locations = location_obj.search([('location_id', 'child_of', location.id),
        #                                        ('usage', '=', 'internal')])
        child_locations = location_obj.search([('location_id', '=', location.id),
                                               ('usage', '=', 'internal')])
        locations += child_locations
        return locations

    @api.multi
    def get_product_available(self, product, from_date=False, to_date=False, location=False,
                              warehouse=False, compute_child=True):
        """ Function to return stock """
        locations = self.get_child_locations(location)
        date_str, date_values = False, False
        where = [tuple(locations.ids), tuple(locations.ids), tuple([product.id])]
        if from_date and to_date:
            date_str = "date::DATE>=%s and date::DATE<=%s"
            where.append(tuple([from_date]))
            where.append(tuple([to_date]))
        elif from_date:
            date_str = "date::DATE>=%s"
            date_values = [from_date]
        elif to_date:
            date_str = "date::DATE<=%s"
            date_values = [to_date]
        if date_values:
            where.append(tuple(date_values))

        # all incoming moves from a location out of the set to a location in the set
        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move
            where location_id NOT IN %s
            and location_dest_id IN %s
            and product_id IN %s and state = 'done' '''
            + (date_str and 'and ' + date_str + ' ' or '') + ' ' + \
            'group by product_id, product_uom', tuple(where))
        results = self._cr.fetchall()
        # all outgoing moves from a location in the set to a location out of the set
        self._cr.execute(
            '''select sum(product_qty), product_id, product_uom 
            from stock_move 
            where location_id IN %s 
            and location_dest_id NOT IN %s 
            and product_id  IN %s and state = 'done' '''
            + (date_str and 'and ' + date_str + ' ' or '') + ' ' + \
            'group by product_id,product_uom', tuple(where))
        results2 = self._cr.fetchall()

        incoming, outgoing = 0, 0
        # Count the incoming quantities
        for quantity, prod_id, prod_uom in results:
            incoming += quantity
        # Count the outgoing quantities
        for quantity, prod_id, prod_uom in results2:
            outgoing += quantity
        return {'incoming': incoming, 'outgoing': outgoing, 'balance': incoming - outgoing}

    @api.multi
    def act_getstockreport(self):
        f_name = '/tmp/stock_report.xlsx'
        workbook = xlsxwriter.Workbook(f_name)
        worksheet = workbook.add_worksheet('Stock Report')
        # Styles
        style_header = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_data = workbook.add_format({
            'border': 1,
            'align': 'left'})
        style_data2 = workbook.add_format({
            'border': 1,
            'align': 'center'})
        style_data3 = workbook.add_format({
            'border': 1,
            'align': 'right'})
        style_total = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header2 = workbook.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter'})
        style_header.set_font_size(18)
        style_header.set_text_wrap()
        style_header.set_bg_color('#d7e4bd')
        style_header.set_font_name('Agency FB')
        style_header.set_border(style=2)
        style_data.set_font_size(12)
        style_data.set_text_wrap()
        style_data.set_font_name('Agency FB')
        style_data2.set_font_size(12)
        style_data2.set_font_name('Agency FB')
        style_data3.set_font_size(12)
        style_data3.set_font_name('Agency FB')
        style_total.set_font_size(12)
        style_total.set_text_wrap()
        style_total.set_border(style=2)
        style_header2.set_font_size(12)
        style_header2.set_bg_color('#d7e4bd')
        style_header2.set_font_name('Agency FB')
        style_header2.set_border(style=2)
        worksheet.set_column(0, 0, 35)
        worksheet.set_column(1, 1, 40)
        worksheet.set_column(2, 2, 12)
        worksheet.set_column(3, 3, 12)
        worksheet.set_column(4, 4, 12)
        worksheet.set_column(5, 5, 12)
        worksheet.set_row(0, 25)

        product_obj = self.env['product.product']
        price_prec = self.env['decimal.precision'].precision_get('Product Price')
        # Getting locations to fetch report for
        locations = self.get_locations()
        locations = self.env['stock.location'].browse(list(set(locations.ids)))
        products = self.product_ids
        if not products:
            products = product_obj.search([])
        row, col = 0, 0
        worksheet.merge_range(row, col + 1, row, col + 2, "Inventory Report", style_header)
        row += 1
        worksheet.write(row, col, 'Company', style_header2)
        worksheet.write(row + 1, col, self.company_id and self.company_id.name or 'ALL', style_data2)
        worksheet.write(row, col + 1, 'Warehouse', style_header2)
        warehouse_name = ''
        if self.warehouse_ids:
            for w in self.warehouse_ids:
                warehouse_name = warehouse_name + w.name + ', '
        else:
            warehouse_name = 'ALL'
        worksheet.write(row + 1, col + 1, warehouse_name, style_data2)
        worksheet.write(row, col + 2, 'Date From', style_header2)
        worksheet.write(row + 1, col + 2, self.from_date or ' ', style_data2)
        worksheet.write(row, col + 3, 'Date To', style_header2)
        worksheet.write(row + 1, col + 3, self.to_date or ' ', style_data2)
        worksheet.write(row, col + 4, ' ', style_header2)
        worksheet.write(row, col + 5, ' ', style_header2)
        row += 2
        col = 0
        worksheet.write(row, col, 'Product', style_header2)
        worksheet.write(row, col + 1, 'Location', style_header2)
        worksheet.write(row, col + 2, 'Opening', style_header2)
        worksheet.write(row, col + 3, 'Recieved', style_header2)
        worksheet.write(row, col + 4, 'Sales', style_header2)
        worksheet.write(row, col + 5, 'Closing', style_header2)
        if self.show_valuation:
            worksheet.write(row, col + 6, 'Valuation', style_header2)
        row += 1
        if self.from_date:
            previous_date = datetime.strptime(
                self.from_date, DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=1)
        for product in products.sorted(lambda p: p.name):
            for location in locations:
                col = 0
                opening_dict = {}
                if self.from_date:
                    opening_dict = self.get_product_available(product, False, previous_date,
                                                              location)
                inventory_dict = self.get_product_available(product, self.from_date, self.to_date,
                                                            location)
                closing_balance = opening_dict.get('balance', 0.0) + inventory_dict.get('balance', 0.0)
                worksheet.write(row, col, product.name_get()[0][1], style_data)
                worksheet.write(row, col + 1, location.complete_name, style_data)
                worksheet.write(row, col + 2, opening_dict.get('balance', 0.0), style_data3)
                worksheet.write(row, col + 3, inventory_dict.get('incoming', 0.0), style_data3)
                worksheet.write(row, col + 4, inventory_dict.get('outgoing', 0.0), style_data3)
                worksheet.write(row, col + 5, closing_balance, style_data3)
                if self.show_valuation:
                    product_costing = round(closing_balance * product.standard_price, price_prec)
                    worksheet.write(row, col + 6, product_costing, style_data3)
                row += 1
        # Writing Total Formula
        col = 0
        worksheet.merge_range(row, col, row, col + 1, "Total", style_total)
        col_length = 6
        if self.show_valuation:
            col_length += 1
        for col in range(2, col_length):
            amount_start = rowcol_to_cell(4, col)
            amount_stop = rowcol_to_cell(row - 1, col)
            formula = '=ROUND(SUM(%s:%s), 0)' % (amount_start, amount_stop)
            worksheet.write_formula(row, col, formula, style_total)
        row += 1
        workbook.close()
        f = open(f_name, 'rb')
        data = f.read()
        f.close()
        name = "%s.xlsx" % ("StockReport_" + str(self.from_date or '') + '-' + str(self.to_date or ''))
        out_wizard = self.env['xlsx.output'].create({'name': name,
                                                     'xls_output': base64.encodebytes(data)})
        view_id = self.env.ref('gts_stock_xlsx_report.xlsx_output_form').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'xlsx.output',
            'target': 'new',
            'view_mode': 'form',
            'res_id': out_wizard.id,
            'views': [[view_id, 'form']],
        }
