from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import Warning
import time
import xlsxwriter
import base64
from odoo import fields, models, api
from cStringIO import StringIO
import pytz
from pytz import timezone
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class StockSummaryNew(models.Model):
    _name = "stock.summary.new"
    _description = "Stock Summary New"

    @api.multi
    def unlink(self):
        for stock in self:
            if stock.state != 'draft':
                raise Warning('Data yang bisa dihapus hanya yg berstatus draft')
        return super(StockSummaryNew, self).unlink()

    @api.multi
    def get_default_date_multi(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))

    @api.multi
    @api.depends('inventory_id.date')
    def get_start_date(self):
        for me_id in self:
            if me_id.inventory_id.accounting_date:
            #     me_id.date_start = me_id.inventory_id.accounting_date
            # else:
                me_id.date_start = me_id.inventory_id.date

    name = fields.Char("Number", copy=False)
    date_adj = fields.Date("Adjustment Date")
    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment')
    company_id = fields.Many2one('res.company', string='Company', related='location_id.company_id')
    date_start = fields.Datetime("Start Date", compute='get_start_date', store=True)
    date_end = fields.Datetime("End Date", required=True, default=lambda *a: time.strftime("%Y-%m-%d"))
    date_end_soh = fields.Datetime("End Date (SOH)", required=True, default=lambda *a: time.strftime("%Y-%m-%d"))
    last_update = fields.Datetime("Last Update", readonly=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True, domain=[('usage', '=', 'internal')])
    summary_line = fields.One2many('stock.summary.line.new', 'summary_id', 'Details', ondelete="cascade")
    summary_line_soh = fields.One2many('stock.summary.line.new.soh', 'summary_id', 'SOH Details', ondelete="cascade")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
    ], 'Status', default='draft')
    user_id = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
    emails = fields.Text(string='Email To', help='Separated by comma')
    file_data = fields.Binary('File', readonly=True)

    @api.multi
    def action_export(self):
        action = self.env.ref('vit_stock_card_pro.report_stock_xlsx_action')
        return {
            'name': action.name + ' In',
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': 'new',
            'res_model': action.res_model,
            'domain': [],
        }

    @api.model
    def create(self, vals):
        if not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('vit.stock_summary')
        return super(StockSummaryNew, self).create(vals)

    @api.multi
    def action_open(self):
        for me_id in self:
            if me_id.state != 'draft':
                continue
            data_exist = self.search([('id', '!=', self.id), ('inventory_id', '=', self.inventory_id.id),
                                      ('location_id', '=', self.location_id.id),('state','=','open')], limit=1)
            if data_exist:
                raise Warning(
                    'Data dengan inventory id dan lokasi yang sama sudah tersedia dan berstatus open (number : %s)' % data_exist.name)
            me_id.state = 'open'
            if not me_id.name:
                me_id.name = self.env['ir.sequence'].next_by_code('vit.stock_summary')

    @api.multi
    def action_set_to_draft(self):
        for me_id in self:
            if me_id.state != 'open':
                continue
            me_id.state = 'draft'

    def execute_query(self, sql, to_return='qty'):
        self._cr.execute(sql)
        result = self._cr.fetchall()
        if not result or result[0] == None or result[0][0] == None:
            if to_return == 'qty':
                return 0
            else:
                return []
        if to_return == 'qty':
            return result[0][0]
        return result

    @api.multi
    def auto_calculate(self):
        #import pdb;pdb.set_trace()
        date_current = self.get_default_date_multi().strftime('%Y-%m-%d')
        summary_ids = self.search([
            ('state', '=', 'open'),
            ('inventory_id', '!=', False),
        ])
        summary_ids = summary_ids.filtered(lambda summary: summary.date_end[:10] < date_current)
        for summary_id in summary_ids:
            summary_id.action_calculate()
            summary_id.write({'date_end': datetime.now()})
            summary_id._cr.commit()

    def get_child_locations(self, location_id):
        ids_location = [location_id.id]
        for child_loc in location_id.location_ids:
            ids_location.extend(self.get_child_locations(child_loc))
        return ids_location

    @api.multi
    def action_calculate_soh(self):
        self.delete_lines_soh()
        for me_id in self:
            print
            "START CALCULATE STOCK SUMMARY SOH============================>> %s" % me_id.name

            if not me_id.inventory_id:
                continue
            date_start = me_id.date_start
            date_end = me_id.date_end_soh

            # cek product yang ada di stock move, pack operation dan stock inventory line
            ids_location = self.get_child_locations(me_id.location_id)
            ids_location = str(tuple(ids_location)).replace(',)', ')')

            query = """
                SELECT
                    product_id
                FROM
                    stock_move
                WHERE
                    state = 'done'
                    and picking_id is null
                    and date >= '%s'
                    and date <= '%s'
                    and (location_id in %s or location_dest_id in %s)
                GROUP BY
                    product_id
            """ % (date_start, date_end, ids_location, ids_location)
            ids_product_tuple = self.execute_query(query, 'id')

            query = """
                SELECT
                    spo.product_id
                FROM
                    stock_pack_operation spo
                JOIN
                    stock_picking sp on sp.id = spo.picking_id
                LEFT JOIN
                    stock_move sm on sm.id = (
                        SELECT
                            id
                        FROM
                            stock_move
                        WHERE
                            picking_id = spo.picking_id and product_id = spo.product_id
                        LIMIT 1
                    )
                WHERE
                    sp.state = 'done'
                    and sm.date >= '%s'
                    and sm.date <= '%s'
                    and (spo.location_id in %s or spo.location_dest_id in %s)
                GROUP BY
                    spo.product_id
            """ % (date_start, date_end, ids_location, ids_location)
            ids_product_tuple += self.execute_query(query, 'id')

            query = """
                SELECT
                    sil.product_id
                FROM
                    stock_inventory_line sil
                JOIN
                    stock_inventory si on si.id = sil.inventory_id
                WHERE
                    sil.inventory_id = %s and sil.location_id in %s
                GROUP BY
                    sil.product_id
            """ % (me_id.inventory_id.id, ids_location)
            ids_product_tuple += self.execute_query(query, 'id')

            t_lines = 0.0
            ids_product = []
            for res in ids_product_tuple:
                if res[0] not in ids_product:
                    ids_product.append(res[0])
                    product = res[0]

                    # langsung looping per product dan cari qty di move dan pack operation
                    product_id = self.env['product.product'].browse(product)
                    if not product_id.active:
                        continue

                    qty_in = 0
                    qty_out = 0

                    # QTY START
                    query = """
                        SELECT
                            sum(product_qty) as qty
                        FROM
                            stock_inventory_line
                        WHERE
                            product_id = %s
                            and location_id in %s
                            and inventory_id = %s
                    """ % (product_id.id, ids_location, me_id.inventory_id.id)
                    qty_start = self.execute_query(query)

                    # QTY IN
                    query = """
                        SELECT
                            sum(product_uom_qty) as qty
                        FROM
                            stock_move
                        WHERE
                            state = 'done'
                            and picking_id is null
                            and date >= '%s'
                            and date <= '%s'
                            and location_dest_id in %s
                            and product_id = %s
                            and inventory_id != %s
                    """ % (date_start, date_end, ids_location, product_id.id, me_id.inventory_id.id)
                    qty_in += self.execute_query(query)

                    query = """
                        SELECT
                            sum(spo.product_qty) as qty
                        FROM
                            stock_pack_operation spo
                        JOIN
                            stock_picking sp on sp.id = spo.picking_id
                        LEFT JOIN
                            stock_move sm on sm.id = (
                                SELECT
                                    id
                                FROM
                                    stock_move
                                WHERE
                                    picking_id = spo.picking_id and product_id = spo.product_id
                                LIMIT 1
                            )
                        WHERE
                            sp.state = 'done'
                            and sm.date >= '%s'
                            and sm.date <= '%s'
                            and spo.location_dest_id in %s
                            and spo.product_id = %s
                    """ % (date_start, date_end, ids_location, product_id.id)
                    qty_in += self.execute_query(query)

                    # QTY OUT
                    query = """
                        SELECT
                            sum(product_uom_qty) as qty
                        FROM
                            stock_move
                        WHERE
                            state = 'done'
                            and picking_id is null
                            and date >= '%s'
                            and date <= '%s'
                            and location_id in %s
                            and product_id = %s
                            and inventory_id != %s
                    """ % (date_start, date_end, ids_location, product_id.id, me_id.inventory_id.id)
                    qty_out += self.execute_query(query)

                    query = """
                        SELECT
                            sum(spo.product_qty) as qty
                        FROM
                            stock_pack_operation spo
                        JOIN
                            stock_picking sp on sp.id = spo.picking_id
                        LEFT JOIN
                            stock_move sm on sm.id = (
                                SELECT
                                    id
                                FROM
                                    stock_move
                                WHERE
                                    picking_id = spo.picking_id and product_id = spo.product_id
                                LIMIT 1
                            )
                        WHERE
                            sp.state = 'done'
                            and sm.date >= '%s'
                            and sm.date <= '%s'
                            and spo.location_id in %s
                            and spo.product_id = %s
                    """ % (date_start, date_end, ids_location, product_id.id)
                    qty_out += self.execute_query(query)
                    # hpp dan hpj insert biasa, ga pake related
                    balance = qty_start + qty_in - qty_out
                    query = """INSERT INTO
                                        stock_summary_line_new_soh(summary_id,product_id,hpj,hpp,qty_available,qty_start,qty_in,qty_out,qty_balance)
                                    VALUES
                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    RETURNING id 
                                """ % (
                    me_id.id, product_id.id, product_id.lst_price, product_id.standard_price, product_id.qty_available,
                    qty_start, qty_in, qty_out, balance)
                    self._cr.execute(query)
                    t_lines += 1.0
                    _logger.info("insert %s stock_summary_line_new_soh %s =============> success" % (str(t_lines),me_id.name))
                    self._cr.commit()

            print
            "FINISH CALCULATE STOCK SUMMARY SOH ============================>> %s" % me_id.name
            me_id.delete_duplicate_summary_line()
            _logger.info("insert Total %s stock_summary_line_new_soh %s =============> successfully" % (str(t_lines), me_id.name))


    @api.multi
    def action_print_soh(self):
        report_name = 'Details Stock Summary SOH %s'%self.name

        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(self.name)

        #konten di sini
        worksheet.set_column('A1:A1', 20)
        worksheet.set_column('B1:B1', 30)
        worksheet.set_column('C1:C1', 40)
        worksheet.set_column('D1:D1', 20)
        worksheet.set_column('E1:E1', 20)
        worksheet.set_column('F1:F1', 20)
        worksheet.set_column('G1:G1', 20)
        worksheet.set_column('H1:H1', 20)
        worksheet.set_column('I1:I1', 20)
        worksheet.set_column('J1:J1', 20)

        worksheet.write('A1', 'Code', wbf['header'])
        worksheet.write('B1', 'Product Name', wbf['header'])
        worksheet.write('C1', 'Product Category', wbf['header'])
        worksheet.write('D1', 'On hand all locations', wbf['header'])
        worksheet.write('E1', 'Start', wbf['header'])
        worksheet.write('F1', 'Qty In', wbf['header'])
        worksheet.write('G1', 'Qty Out', wbf['header'])
        worksheet.write('H1', 'Balance', wbf['header'])
        worksheet.write('I1', 'HPP', wbf['header'])
        worksheet.write('J1', 'HPJ', wbf['header'])
        row = 2
        for line in self.summary_line_soh :
            # worksheet.write('A%s' % row, line.product_id.name_get()[0][1], wbf['content'])
            worksheet.write('A%s' % row, line.product_id.default_code, wbf['content'])
            worksheet.write('B%s'%row, line.product_id.name, wbf['content'])
            worksheet.write('C%s' % row, line.product_id.categ_id.name_get()[0][1], wbf['content'])
            worksheet.write('D%s'%row, line.qty_available, wbf['content_float'])
            worksheet.write('E%s'%row, line.qty_start, wbf['content_float'])
            worksheet.write('F%s'%row, line.qty_in, wbf['content_float'])
            worksheet.write('G%s'%row, line.qty_out, wbf['content_float'])
            worksheet.write('H%s'%row, line.qty_balance, wbf['content_float'])
            worksheet.write('I%s'%row, line.hpp, wbf['content_float'])
            worksheet.write('J%s'%row, line.hpj, wbf['content_float'])
            row += 1

        worksheet.merge_range('A%s:C%s' %(row,row), 'Total', wbf['header_no'])
        worksheet.write_formula('D%s' %row, '{=subtotal(9,D2:D%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('E%s' %row, '{=subtotal(9,E2:E%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('F%s' %row, '{=subtotal(9,F2:F%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('G%s' %row, '{=subtotal(9,G2:G%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('H%s' %row, '{=subtotal(9,H2:H%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('I%s' %row, '{=subtotal(9,I2:I%s)}'%(row-1), wbf['total_float'])
        worksheet.write_formula('J%s' %row, '{=subtotal(9,J2:J%s)}'%(row-1), wbf['total_float'])
        #sampai sini

        workbook.close()
        result = base64.encodestring(fp.getvalue())
        date_string = self.date_end_soh
        filename = '%s %s'%(report_name,date_string)
        filename += '%2Exlsx'
        self.write({'file_data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=file_data&download=true&filename="+filename
        return {
            'name': 'Stock Summary SOH',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }


    @api.multi
    def action_calculate(self):
        now = fields.Datetime.now()[11:]
        if now > '01:00:00' < '09:30:00' and self.env.uid != SUPERUSER_ID:
            raise Warning('Calculate manual hanya bisa dilakukan pada pukul 17:30 s/d 08:00 WIB')
        self.delete_lines()
        for me_id in self:
            print
            "START CALCULATE STOCK SUMMARY ============================>> %s" % me_id.name

            if me_id.state != 'open' or not me_id.inventory_id:
                continue
            date_start = me_id.date_start
            date_end = me_id.date_end

            # cek product yang ada di stock move, pack operation dan stock inventory line
            ids_location = self.get_child_locations(me_id.location_id)
            ids_location = str(tuple(ids_location)).replace(',)', ')')

            query = """
                SELECT
                    product_id
                FROM
                    stock_move
                WHERE
                    state = 'done'
                    and picking_id is null
                    and date >= '%s'
                    and date <= '%s'
                    and (location_id in %s or location_dest_id in %s)
                GROUP BY
                    product_id
            """ % (date_start, date_end, ids_location, ids_location)
            ids_product_tuple = self.execute_query(query, 'id')

            query = """
                SELECT
                    spo.product_id
                FROM
                    stock_pack_operation spo
                JOIN
                    stock_picking sp on sp.id = spo.picking_id
                LEFT JOIN
                    stock_move sm on sm.id = (
                        SELECT
                            id
                        FROM
                            stock_move
                        WHERE
                            picking_id = spo.picking_id and product_id = spo.product_id
                        LIMIT 1
                    )
                WHERE
                    sp.state = 'done'
                    and sm.date >= '%s'
                    and sm.date <= '%s'
                    and (spo.location_id in %s or spo.location_dest_id in %s)
                GROUP BY
                    spo.product_id
            """ % (date_start, date_end, ids_location, ids_location)
            ids_product_tuple += self.execute_query(query, 'id')

            query = """
                SELECT
                    sil.product_id
                FROM
                    stock_inventory_line sil
                JOIN
                    stock_inventory si on si.id = sil.inventory_id
                WHERE
                    sil.inventory_id = %s and sil.location_id in %s
                GROUP BY
                    sil.product_id
            """ % (me_id.inventory_id.id, ids_location)
            ids_product_tuple += self.execute_query(query, 'id')
            t_lines = 1.0
            ids_product = []
            for res in ids_product_tuple:
                if res[0] not in ids_product:
                    ids_product.append(res[0])
                    product = res[0]

                    # langsung looping per product dan cari qty di move dan pack operation
                    product_id = self.env['product.product'].browse(product)
                    #product_ids = product_ids.filtered(lambda prod: prod.active)
                    if not product_id.active :
                        continue
                    qty_in = 0
                    qty_out = 0

                    # QTY START
                    query = """
                        SELECT
                            sum(product_qty) as qty
                        FROM
                            stock_inventory_line
                        WHERE
                            product_id = %s
                            and location_id in %s
                            and inventory_id = %s
                    """ % (product_id.id, ids_location, me_id.inventory_id.id)
                    qty_start = self.execute_query(query)

                    # QTY IN
                    query = """
                        SELECT
                            sum(product_uom_qty) as qty
                        FROM
                            stock_move
                        WHERE
                            state = 'done'
                            and picking_id is null
                            and date >= '%s'
                            and date <= '%s'
                            and location_dest_id in %s
                            and product_id = %s
                            and inventory_id != %s
                    """ % (date_start, date_end, ids_location, product_id.id, me_id.inventory_id.id)
                    qty_in += self.execute_query(query)

                    query = """
                        SELECT
                            sum(spo.product_qty) as qty
                        FROM
                            stock_pack_operation spo
                        JOIN
                            stock_picking sp on sp.id = spo.picking_id
                        LEFT JOIN
                            stock_move sm on sm.id = (
                                SELECT
                                    id
                                FROM
                                    stock_move
                                WHERE
                                    picking_id = spo.picking_id and product_id = spo.product_id
                                LIMIT 1
                            )
                        WHERE
                            sp.state = 'done'
                            and sm.date >= '%s'
                            and sm.date <= '%s'
                            and spo.location_dest_id in %s
                            and spo.product_id = %s
                    """ % (date_start, date_end, ids_location, product_id.id)
                    qty_in += self.execute_query(query)

                    # QTY OUT
                    query = """
                        SELECT
                            sum(product_uom_qty) as qty
                        FROM
                            stock_move
                        WHERE
                            state = 'done'
                            and picking_id is null
                            and date >= '%s'
                            and date <= '%s'
                            and location_id in %s
                            and product_id = %s
                            and inventory_id != %s
                    """ % (date_start, date_end, ids_location, product_id.id, me_id.inventory_id.id)
                    qty_out += self.execute_query(query)

                    query = """
                        SELECT
                            sum(spo.product_qty) as qty
                        FROM
                            stock_pack_operation spo
                        JOIN
                            stock_picking sp on sp.id = spo.picking_id
                        LEFT JOIN
                            stock_move sm on sm.id = (
                                SELECT
                                    id
                                FROM
                                    stock_move
                                WHERE
                                    picking_id = spo.picking_id and product_id = spo.product_id
                                LIMIT 1
                            )
                        WHERE
                            sp.state = 'done'
                            and sm.date >= '%s'
                            and sm.date <= '%s'
                            and spo.location_id in %s
                            and spo.product_id = %s
                    """ % (date_start, date_end, ids_location, product_id.id)
                    qty_out += self.execute_query(query)
                    # hpp dan hpj insert biasa, ga pake related
                    # summary_line_id = self.env['stock.summary.line.new'].create({
                    #                 #     'summary_id': me_id.id,
                    #                 #     'product_id': product_id.id,
                    #                 #     'hpj' : product_id.lst_price,
                    #                 #     'hpp' : product_id.standard_price,
                    #                 #     'qty_available': product_id.qty_available,
                    #                 #     'qty_start': qty_start,
                    #                 #     'qty_in': qty_in,
                    #                 #     'qty_out': qty_out,
                    #                 #     'qty_balance': qty_start + qty_in - qty_out,
                    #                 # })
                    balance = qty_start + qty_in - qty_out
                    # import pdb;pdb.set_trace()
                    query = """INSERT INTO
                                        stock_summary_line_new(summary_id,product_id,hpj,hpp,qty_available,qty_start,qty_in,qty_out,qty_balance)
                                    VALUES
                                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    RETURNING id 
                                """ % (
                    me_id.id, product_id.id, product_id.lst_price, product_id.standard_price, product_id.qty_available,
                    qty_start, qty_in, qty_out, balance)
                    self._cr.execute(query)
                    summary_line_id = self.env['stock.summary.line.new'].browse(self._cr.fetchone()[0])
                    t_lines += 1.0
                    _logger.info("insert %s stock_summary_line_new %s =============> success" % (str(t_lines),me_id.name))
                    self.create_history(me_id, summary_line_id, date_start, date_end, ids_location, product_id,
                                        me_id.inventory_id)
                    _logger.info("insert stock_summary_line_new_history %s =============> success" % (me_id.name))
            me_id.last_update = datetime.now()
            print
            "FINISH CALCULATE STOCK SUMMARY ============================>> %s" % me_id.name
            _logger.info("insert total %s stock_summary_line_new %s =============> successfully" % (str(t_lines), me_id.name))

    @api.multi
    def create_history(self, summary_id, summary_line_id, date_start, date_end, ids_location, product_id, inventory_id):
        values = []

        # HISTORY IN
        query = """
            SELECT
                name,
                date,
                product_uom_qty as qty,
                'in' as type,
                'move' as source,
                id as transaction_id
            FROM
                stock_move
            WHERE
                state = 'done'
                and picking_id is null
                and date >= '%s'
                and date <= '%s'
                and location_dest_id in %s
                and product_id = %s
                and inventory_id != %s
        """ % (date_start, date_end, ids_location, product_id.id, inventory_id.id)
        self._cr.execute(query)
        datas = self._cr.dictfetchall()
        if datas:
            values += datas

        query = """
            SELECT
                sp.name,
                sm.date,
                spo.product_qty as qty,
                'in' as type,
                'operation' as source,
                spo.id as transaction_id
            FROM
                stock_pack_operation spo
            JOIN
                stock_picking sp on sp.id = spo.picking_id
            LEFT JOIN
                stock_move sm on sm.id = (
                    SELECT
                        id
                    FROM
                        stock_move
                    WHERE
                        picking_id = spo.picking_id and product_id = spo.product_id
                    LIMIT 1
                )
            WHERE
                sp.state = 'done'
                and sm.date >= '%s'
                and sm.date <= '%s'
                and spo.location_dest_id in %s
                and spo.product_id = %s
        """ % (date_start, date_end, ids_location, product_id.id)
        self._cr.execute(query)
        datas = self._cr.dictfetchall()
        if datas:
            values += datas

        # HISTORY OUT
        query = """
            SELECT
                name,
                date,
                product_uom_qty as qty,
                'out' as type,
                'move' as source,
                id as transaction_id
            FROM
                stock_move
            WHERE
                state = 'done'
                and picking_id is null
                and date >= '%s'
                and date <= '%s'
                and location_id in %s
                and product_id = %s
                and inventory_id != %s
        """ % (date_start, date_end, ids_location, product_id.id, inventory_id.id)
        self._cr.execute(query)
        datas = self._cr.dictfetchall()
        if datas:
            values += datas

        query = """
            SELECT
                sp.name,
                sm.date,
                spo.product_qty as qty,
                'out' as type,
                'operation' as source,
                spo.id as transaction_id
            FROM
                stock_pack_operation spo
            JOIN
                stock_picking sp on sp.id = spo.picking_id
            LEFT JOIN
                stock_move sm on sm.id = (
                    SELECT
                        id
                    FROM
                        stock_move
                    WHERE
                        picking_id = spo.picking_id and product_id = spo.product_id
                    LIMIT 1
                )
            WHERE
                sp.state = 'done'
                and sm.date >= '%s'
                and sm.date <= '%s'
                and spo.location_id in %s
                and spo.product_id = %s
        """ % (date_start, date_end, ids_location, product_id.id)
        self._cr.execute(query)
        datas = self._cr.dictfetchall()
        if datas:
            values += datas
        for val in values:
            # self.env['stock.summary.line.new.history'].create({
            #     'summary_id': summary_id.id,
            #     'summary_line_id': summary_line_id.id,
            #     'name': val['name'] if val['name'] else '',
            #     'date': val['date'],
            #     'qty': val['qty'],
            #     'type': val['type'],
            #     'source': val['source'],
            #     'transaction_id': val['transaction_id'],
            # })
            query = """
                INSERT INTO
                    stock_summary_line_new_history(summary_id,summary_line_id,name,date,qty,type,source,transaction_id,product_code,price,total)
                VALUES
                    (%s, %s, '%s', '%s', %s, '%s', '%s', %s, '%s', %s, %s)
            """ % (summary_id.id, summary_line_id.id, val['name'], val['date'], val['qty'], val['type'], val['source'],
                   val['transaction_id'], summary_line_id.product_id.default_code,
                   summary_line_id.product_id.standard_price if val[
                                                                    'type'] == 'in' else summary_line_id.product_id.lst_price,
                   summary_line_id.product_id.standard_price * val['qty'] if val[
                                                                                 'type'] == 'in' else summary_line_id.product_id.lst_price *
                                                                                                      val['qty'])
            self._cr.execute(query)

    @api.multi
    def delete_lines(self):
        if not self:
            return False
        self._cr.execute("""
            delete from stock_summary_line_new where summary_id in %s
        """ % (str(tuple(self.ids)).replace(',)', ')')))


    @api.multi
    def delete_duplicate_summary_line(self):
        if not self:
            return False
        self._cr.execute("""
            DELETE 
                FROM
                    stock_summary_line_new_soh a
                USING
                    stock_summary_line_new_soh b
            WHERE
                a.id < b.id
                AND
                a.product_id = b.product_id
                AND a.summary_id in %s 
        """ % (str(tuple(self.ids)).replace(',)', ')')))


    @api.multi
    def delete_lines_soh(self):
        if not self:
            return False
        self._cr.execute("""
            delete from stock_summary_line_new_soh where summary_id in %s
        """ % (str(tuple(self.ids)).replace(',)', ')')))

    @api.multi
    def view_qty_in(self):
        history_ids = self.env['stock.summary.line.new.history'].search([
            ('summary_id', '=', self.id),
            ('type', '=', 'in')
        ])
        action = self.env.ref('vit_stock_card_pro.stock_summary_line_new_history_action')
        return {
            'name': action.name + ' In',
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': [('id', 'in', history_ids.ids)],
        }

    @api.multi
    def view_qty_out(self):
        history_ids = self.env['stock.summary.line.new.history'].search([
            ('summary_id', '=', self.id),
            ('type', '=', 'out')
        ])
        action = self.env.ref('vit_stock_card_pro.stock_summary_line_new_history_action')
        return {
            'name': action.name + ' Out',
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': [('id', 'in', history_ids.ids)],
        }

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['orange'], 'font_color': '#000000'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000'})
        wbf['header_yellow'].set_border()

        wbf['header_no'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align': 'left'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()

        wbf['title_doc'] = workbook.add_format({'bold': 1, 'align': 'left'})
        wbf['title_doc'].set_font_size(12)

        wbf['company'] = workbook.add_format({'align': 'left'})
        wbf['company'].set_font_size(11)

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()

        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()

        wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()

        wbf['total_float'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'right', 'num_format': '#,##0.00'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total_number'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['white_orange'], 'bold': 1, 'num_format': '#,##0'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()

        wbf['total'] = workbook.add_format({'bold': 1, 'bg_color': colors['white_orange'], 'align': 'center'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()

        wbf['total_number_yellow'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()

        wbf['total_yellow'] = workbook.add_format({'bold': 1, 'bg_color': colors['yellow'], 'align': 'center'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()

        wbf['total_number_orange'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()

        wbf['total_orange'] = workbook.add_format({'bold': 1, 'bg_color': colors['orange'], 'align': 'center'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()

        wbf['header_detail_space'] = workbook.add_format({})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()

        return wbf, workbook

    @api.multi
    def send_stock_summary_mail(self):

        auto_email_ids = self.search([('state', '=', 'open'), ('emails', '!=', False)])
        for summary_id in auto_email_ids:
            try:
                recipients = summary_id.emails.replace(' ', '')
                recipients = recipients.replace("""
    """, '')
                report_name = 'Stock Summary %s ' % summary_id.name

                fp = StringIO()
                workbook = xlsxwriter.Workbook(fp)
                wbf, workbook = summary_id.add_workbook_format(workbook)
                worksheet = workbook.add_worksheet(summary_id.name)

                worksheet.set_column('A1:A1', 20)
                worksheet.set_column('B1:B1', 30)
                worksheet.set_column('C1:C1', 40)
                worksheet.set_column('D1:D1', 20)
                worksheet.set_column('E1:E1', 20)
                worksheet.set_column('F1:F1', 20)
                worksheet.set_column('G1:G1', 20)
                worksheet.set_column('H1:H1', 20)
                worksheet.set_column('I1:I1', 20)
                worksheet.set_column('J1:J1', 20)

                worksheet.write('A1', 'Code', wbf['header'])
                worksheet.write('B1', 'Product Name', wbf['header'])
                worksheet.write('C1', 'Product Category', wbf['header'])
                worksheet.write('D1', 'On hand all locations', wbf['header'])
                worksheet.write('E1', 'Start', wbf['header'])
                worksheet.write('F1', 'Qty In', wbf['header'])
                worksheet.write('G1', 'Qty Out', wbf['header'])
                worksheet.write('H1', 'Balance', wbf['header'])
                worksheet.write('I1', 'HPP', wbf['header'])
                worksheet.write('J1', 'HPJ', wbf['header'])
                row = 2
                for line in summary_id.summary_line:
                    # worksheet.write('A%s' % row, line.product_id.name_get()[0][1], wbf['content'])
                    worksheet.write('A%s' % row, line.product_id.default_code, wbf['content'])
                    worksheet.write('B%s' % row, line.product_id.name, wbf['content'])
                    worksheet.write('C%s' % row, line.product_id.categ_id.name_get()[0][1], wbf['content'])
                    worksheet.write('D%s' % row, line.qty_available, wbf['content_float'])
                    worksheet.write('E%s' % row, line.qty_start, wbf['content_float'])
                    worksheet.write('F%s' % row, line.qty_in, wbf['content_float'])
                    worksheet.write('G%s' % row, line.qty_out, wbf['content_float'])
                    worksheet.write('H%s' % row, line.qty_balance, wbf['content_float'])
                    worksheet.write('I%s' % row, line.hpp, wbf['content_float'])
                    worksheet.write('J%s' % row, line.hpj, wbf['content_float'])
                    row += 1

                worksheet.merge_range('A%s:C%s' % (row, row), 'Total', wbf['header_no'])
                worksheet.write_formula('D%s' % row, '{=subtotal(9,D2:D%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('E%s' % row, '{=subtotal(9,E2:E%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('F%s' % row, '{=subtotal(9,F2:F%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('G%s' % row, '{=subtotal(9,G2:G%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('H%s' % row, '{=subtotal(9,H2:H%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('I%s' % row, '{=subtotal(9,I2:I%s)}' % (row - 1), wbf['total_float'])
                worksheet.write_formula('J%s' % row, '{=subtotal(9,J2:J%s)}' % (row - 1), wbf['total_float'])
                # import pdb;pdb.set_trace()
                workbook.close()
                result = base64.encodestring(fp.getvalue())
                date_string = summary_id.date_end
                filename = '%s (%s)' % (report_name, date_string)
                filename += '%2Exlsx'
                newfilename = '%s (%s)' % (report_name, date_string[:10])
                attachment_id = self.env['ir.attachment'].create({
                    'name': 'Stock Summary : %s.xlsx' % newfilename,
                    'type': 'binary',
                    'datas': result,
                    'datas_fname': 'Stock Summary : %s.xlsx' % newfilename,
                    'res_model': 'stock.summary.new',
                    'res_id': summary_id.id,
                    'public': True,
                })

                mail_id = self.env['mail.mail'].create({
                    'subject': 'Stock Summary  : %s ' % newfilename,
                    'body_html': '',
                    'attachment_ids': [(4, attachment_id.ids)],
                    'reply_to': False,
                    'email_from': 'noreply@shafco.com',
                    'email_to': recipients,
                })

                mail_id.send()
                mail_id._cr.commit()
            except:
                continue


class StockSummaryLineNew(models.Model):
    _name = "stock.summary.line.new"
    _description = "Stock Summary Line New"
    _rec_name = "product_id"

    summary_id = fields.Many2one('stock.summary.new', string='Stock Summary', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    location_id = fields.Many2one('stock.location', string='Location', related='summary_id.location_id', store=True)
    qty_available = fields.Float("On hand all locations")
    qty_start = fields.Float("Start")
    qty_in = fields.Float("Qty In")
    qty_out = fields.Float("Qty Out")
    qty_balance = fields.Float("Balance")
    hpj = fields.Float("HPJ")
    hpp = fields.Float("HPP")
    date_start = fields.Datetime("Start Date", related='summary_id.date_start', store=True)
    date_end = fields.Datetime("End Date", related='summary_id.date_end', store=True)
    history_in_ids = fields.One2many('stock.summary.line.new.history', 'summary_line_id', domain=[('type', '=', 'in')])
    history_out_ids = fields.One2many('stock.summary.line.new.history', 'summary_line_id',
                                      domain=[('type', '=', 'out')])

StockSummaryLineNew()


class StockSummaryLineNewSOH(models.Model):
    _name = "stock.summary.line.new.soh"
    _description = "Stock Summary Line New SOH"
    _rec_name = "product_id"

    summary_id = fields.Many2one('stock.summary.new', string='Stock Summary', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    location_id = fields.Many2one('stock.location', string='Location', related='summary_id.location_id', store=True)
    qty_available = fields.Float("On hand all locations")
    qty_start = fields.Float("Start")
    qty_in = fields.Float("Qty In")
    qty_out = fields.Float("Qty Out")
    qty_balance = fields.Float("Balance")
    hpj = fields.Float("HPJ")
    hpp = fields.Float("HPP")
    date_start = fields.Datetime("Start Date", related='summary_id.date_start', store=True)
    date_end = fields.Datetime("End Date", related='summary_id.date_end_soh', store=True)

StockSummaryLineNewSOH()


class StockSummaryLineNewHistory(models.Model):
    _name = "stock.summary.line.new.history"
    _description = "History Stock Summary Line New"

    @api.depends('type', 'qty', 'summary_line_id.product_id')
    @api.multi
    def _get_amount(self):
        for me_id in self:
            if me_id.type == 'in':
                price = me_id.summary_line_id.product_id.standard_price
            else:
                price = me_id.summary_line_id.product_id.lst_price
            me_id.price = price
            me_id.total = price * me_id.qty

    summary_line_id = fields.Many2one('stock.summary.line.new', string='Product', ondelete='cascade')
    summary_id = fields.Many2one('stock.summary.new', string='Stock Summary', related='summary_line_id.summary_id',
                                 store=True)
    name = fields.Char(string='No Transaksi')
    date = fields.Datetime(string='Tanggal')
    product_code = fields.Char(string='Kode Barang', related='summary_line_id.product_id.default_code', store=True)
    qty = fields.Float(string='Qty')
    price = fields.Float(string='Harga', compute='_get_amount', store=True)
    total = fields.Float(string='Total', compute='_get_amount', store=True)
    type = fields.Selection([
        ('in', 'in'),
        ('out', 'out')
    ], string='Transaction Type')
    source = fields.Selection([
        ('move', 'Stock Move'),
        ('operation', 'Stock Pak Operations')
    ], string='Transaction Type')
    transaction_id = fields.Integer(string='Transaction ID')

StockSummaryLineNewHistory()


class StockLocation(models.Model):
    _inherit = 'stock.location'

    location_ids = fields.One2many('stock.location', 'location_id', string='Locations')

StockLocation()