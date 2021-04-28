from odoo import api, fields, models, _
from datetime import date
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import base64
import xlwt
from io import BytesIO
from xlrd import open_workbook

SC_STATES = [('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')]

class stock_summary(models.Model):
    _name = "vit.stock_summary"
    _rec_name = "location_id"

    @api.multi
    def unlink(self):
        for stock in self:
            if stock.state != 'draft' :
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus draft'))
        return super(stock_summary, self).unlink()

    ref				= fields.Char("Number")
    date_start		= fields.Date("Date Start", required=True, default=fields.Date.today())
    date_end		= fields.Date("Date End", required=True, default=fields.Date.today())
    location_id		= fields.Many2one('stock.location', 'Location', required=True)
    line_ids		= fields.One2many( 'vit.stock_summary_line', 'stock_summary_id','Details', ondelete="cascade")
    breakdown_sn	= fields.Boolean("Breakdown Lot/Serial Number?")
    state			= fields.Selection( SC_STATES, 'Status',readonly= True,required=True, default="draft")
    user_id			= fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)
    name            = fields.Char('File Name', readonly=True)
    name_txt_file   = fields.Char('File Name', readonly=True)
    export_data     = fields.Binary("Export File")
    export_data_txt = fields.Binary("Export File")

    @api.multi
    def action_calculate(self):
        # kosongkan stock_summary_line
        # cari list produk yang ada stocknya di location id
        # cari stock move product_id dan location_id, start_date to end_date
        # insert into stock_summary_line
        # jika keluar dari location (source_id) maka isi ke qty_out
        # jika masu ke location (dest_id) maka isi ke qty_in
        # hitung qty_balance = qty_start + qty_in - qty_out
        # start balance dihitung dari total qty stock move sebelum start_date

        cr = self.env.cr
        sc = self

        cr.execute("delete from vit_stock_summary_line where stock_summary_id=%s" % sc.id)

        if sc.breakdown_sn:
            self.beginning_lines_sn()
            self.mutasi_lines_sn()
        else:
            self.beginning_lines_nosn()
            self.mutasi_lines_nosn()

        self.update_balance()
        return

    def beginning_lines_sn(self):
        date = "date < '%s 24:00:00'" % (self.date_start)
        line_type = "beg"
        self.process_lines_sn(line_type, date)

    def mutasi_lines_sn(self):
        date = "m.date >= '%s 00:00:00' and m.date <= '%s 24:00:00'" % (self.date_start, self.date_end)
        line_type = "mut"
        self.process_lines_sn(line_type, date)


    def process_lines_sn(self, line_type, date):

        sql = "select m.product_id, m.product_uom, qm.lot_id, sum(qm.product_qty)\
                from \
                stock_move_line qm \
                join stock_move m on m.id=qm.move_id \
                where %s \
                and %s \
                group by qm.lot_id,m.product_id,m.product_uom  \
                order by m.product_id "

        location = self.location_id.id
        locations = self.env['stock.location'].search([('id', 'child_of', [location])])
        ids_location = tuple(locations.ids)
        obj1 = str(ids_location).replace(',)',')')
        # obj1 = ','.join(x for x in mylist_loc)

        ##########################################################################
        # fill product
        ##########################################################################
        if line_type == "beg":
            self.fill_product_data(sql)
            self.update_starting(sql)

        ##########################################################################
        # update incoming
        # update outgoing
        ##########################################################################
        if line_type == "mut":
            self.update_incoming(sql,obj1)
            self.update_outgoing(sql,obj1)

        return

    def fill_product_data(self, sql):
        cr =self.env.cr
        stock_summary_line = self.env['vit.stock_summary_line']

        date = "m.date <= '%s 24:00:00'" % (self.date_end)
        loc = "(m.location_id = %s or m.location_dest_id=%s)" % (self.location_id.id, self.location_id.id)
        cr.execute(sql % (date, loc))
        res = cr.fetchall()
        if not res or res[0] == None:
            return False
        for beg in res:
            product_id 		= beg[0]
            product_uom_id	= beg[1]
            lot_id 			= beg[2]
            qty 			= beg[3]
            data = {
                "stock_summary_id"	: self.id,
                "product_id"		: product_id,
                "product_uom_id"	: product_uom_id,
                "lot_id"			: lot_id,
            }
            stock_summary_line.create(data)

    def update_starting(self, sql):
        cr =self.env.cr
        date = "m.date < '%s 00:00:00'" % (self.date_start)
        loc = "m.location_dest_id=%s" % (self.location_id.id)
        cr.execute(sql % (date, loc))
        res = cr.fetchall()
        if not res or res[0] == None:
            return False
        for beg in res:
            product_id 		= beg[0]
            sm_uom_id		= beg[1]
            lot_id 			= beg[2]
            if lot_id is None:
                lot_id = " is null"
            else:
                lot_id = "=%s"  % (lot_id)
            qty 			= beg[3]

            qty, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id,qty)

            sql2 = "update vit_stock_summary_line set \
                        qty_start = %s \
                        where stock_summary_id=%s and product_id=%s and lot_id %s" % \
                   (qty, self.id, product_id, lot_id)
            cr.execute(sql2)

    def update_incoming(self, sql, obj1):
        # import pdb;pdb.set_trace()
        cr =self.env.cr
        date = "m.date >= '%s 00:00:00' and m.date <= '%s 24:00:00'" % (self.date_start, self.date_end)
        loc = "m.location_dest_id in %s " % (obj1)
        cr.execute(sql % (date, loc))
        res = cr.fetchall()
        if not res or res[0] is None:
            return False
        for beg in res:
            product_id      = beg[0]
            sm_uom_id       = beg[1]
            lot_id          = beg[2]
            if lot_id is None:
                lot_id = " is null"
            else:
                lot_id = "=%s"  % (lot_id)
            qty             = beg[3]

            qty, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id,qty)
            product = self.env['product.product'].browse(product_id)

            sql2 = "update vit_stock_summary_line set \
                        qty_in = %s\
                        where stock_summary_id=%s and product_id=%s and lot_id %s" % \
                   (qty, self.id, product_id, lot_id)
            cr.execute(sql2)

    def update_outgoing(self, sql, obj1):
        cr =self.env.cr
        date = "m.date >= '%s 00:00:00' and m.date <= '%s 24:00:00'" % (self.date_start, self.date_end)
        loc = "m.location_id in %s " % (obj1)
        cr.execute(sql % (date, loc))
        res = cr.fetchall()
        if not res or res[0] is None:
            return False
        for beg in res:
            product_id      = beg[0]
            sm_uom_id       = beg[1]
            lot_id          = beg[2]
            if lot_id is None:
                lot_id = " is null"
            else:
                lot_id = "=%s"  % (lot_id)
            qty             = beg[3]

            qty, product_uom_id = self.convert_uom_qty(product_id, sm_uom_id,qty)

            sql2 = "update vit_stock_summary_line set \
                        qty_out = %s \
                        where stock_summary_id=%s and product_id=%s and lot_id %s" % \
                   (qty, self.id, product_id, lot_id)
            cr.execute(sql2)

    def beginning_lines_nosn(self):
        date = "date < '%s 24:00:00'" % (self.date_start)
        line_type = "beg"
        self.process_lines_nosn(line_type, date)



    def mutasi_lines_nosn(self):
        date = "date >= '%s 00:00:00' and date <= '%s 24:00:00'" % (self.date_start, self.date_end)
        line_type = "mut"
        self.process_lines_nosn(line_type, date)


    def process_lines_nosn(self, line_type, date):
        cr =self.env.cr
        stock_summary_line = self.env['vit.stock_summary_line']

        sql = "select product_id,\
                    product_uom,\
                    sum(product_qty) \
                    from stock_move as m \
                    where %s and %s in %s \
                    and state = 'done' \
                    group by product_id,product_uom \
                    order by product_id"

        location = self.location_id.id
        locations = self.env['stock.location'].search([('id', 'child_of', [location])])
        ids_location = tuple(locations.ids)
        obj1 = str(ids_location).replace(',)',')')
        # incoming
        cr.execute(sql % (date, "location_dest_id", obj1))
        res = cr.fetchall()
        if not res or res[0] == 'None':
            return

        if line_type=="beg":
            for beg in res:
                product_id = beg[0]
                sm_uom_id = beg[1]
                qty = beg[2]
                qty,product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty )
                data = {
                    "stock_summary_id"  : self.id,
                    "product_id"        : product_id,
                    "product_uom_id"    : product_uom_id,
                    "qty_start"         : qty,
                    "qty_in"            : 0,
                    "qty_out"           : 0,
                    "qty_balance"       : 0,
                }
                stock_summary_line.create(data)
        else:
            for incoming in res:
                product_id = incoming[0]
                sm_uom_id = incoming[1]
                qty = incoming[2]
                qty,product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty )


                if not stock_summary_line.search([('stock_summary_id','=',self.id),('product_id','=',product_id)]):
                    data = {
                        "stock_summary_id": self.id,
                        "product_id": product_id,
                        "product_uom_id": product_uom_id,
                        "qty_start": 0,
                        "qty_in": qty,
                        "qty_out": 0,
                        "qty_balance": 0,
                    }
                    stock_summary_line.create(data)
                else:
                    sql2 = "update vit_stock_summary_line set \
                                    qty_in = %s \
                                    where stock_summary_id = %s and product_id=%s" % (qty, self.id, product_id)
                    cr.execute(sql2)


        # outgoing
        cr.execute(sql % (date, "location_id", obj1))
        res = cr.fetchall()
        if not res or res[0] == 'None':
            return

        if line_type=="beg":
            for beg in res:
                product_id = beg[0]
                sm_uom_id = beg[1]
                qty = beg[2]
                qty,product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty )
                sql2 = "update vit_stock_summary_line set \
                            qty_start = qty_start - %s \
                            where stock_summary_id = %s and product_id=%s" % (
                    qty, self.id ,product_id )
                cr.execute(sql2)
        else:
            for outgoing in res:
                product_id = outgoing[0]
                sm_uom_id = outgoing[1]
                qty = abs(outgoing[2])
                qty,product_uom_id = self.convert_uom_qty(product_id, sm_uom_id, qty )
                if not stock_summary_line.search([('stock_summary_id','=',self.id),('product_id','=',product_id)]):
                    data = {
                        "stock_summary_id": self.id,
                        "product_id": product_id,
                        "product_uom_id": product_uom_id,
                        "qty_start": 0,
                        "qty_in": 0,
                        "qty_out": qty,
                        "qty_balance": 0,
                    }
                    stock_summary_line.create(data)
                else:
                    sql2 = "update vit_stock_summary_line set \
                            qty_out = %s \
                            where stock_summary_id = %s and product_id=%s" % (
                    qty, self.id, product_id)
                    cr.execute(sql2)

        # balance
        sql = "update vit_stock_summary_line set qty_balance = qty_start + qty_in - qty_out \
            where stock_summary_id = %s " % (self.id)
        cr.execute(sql)

    def convert_uom_qty(self, product_id,sm_uom_id,qty):

        product = self.env['product.product'].browse(product_id)
        uom 	= self.env['uom.uom'].browse(sm_uom_id)

        # if product_id == 45:
        #     # print 'ini'
        if uom.id != product.uom_id.id:
            factor = product.uom_id.factor / uom.factor
        else:
            factor = 1.0

        converted_qty = qty * factor

        return converted_qty, product.uom_id.id

    def update_balance(self):
        cr =self.env.cr
        sql3 = "update vit_stock_summary_line set \
            qty_balance =  coalesce( qty_start,0) +  coalesce(qty_in,0) -  coalesce(qty_out,0) \
            where stock_summary_id = %s " % (self.id)
        cr.execute(sql3)

    @api.multi
    def action_draft(self):
        # set to "draft" state
        return self.write({'state' :SC_STATES[0][0]})

    @api.multi
    def action_confirm(self):
        # set to "confirmed" state
        return self.write({'state' :SC_STATES[1][0]})

    @api.multi
    def action_done(self):
        # set to "done" state
        return self.write({'state' :SC_STATES[2][0]})

    @api.model
    def create(self, vals):

        vals['ref']=self.env['ir.sequence'].next_by_code('vit.stock_summary')
        new_id = super(stock_summary, self).create(vals)
        return new_id

    def cron_action_calculate(self):
        stock_summary_exist = self.search([('state','=','open')])
        for card in stock_summary_exist :
            date_now = date.today()
            card.write({'date_end':date_now})
            card.action_calculate()
            self._cr.commit()
            info = 'Stock Summary '+str(card.ref)+' Updated..'
            # print info
    @api.multi
    def export(self):
        header_name = [
            'Lot/Serial Number',
            'Description',
            'Start',
            'Qty In',
            'Qty Out',
            'Balance',
            'UoM',
        ]
        workbook = xlwt.Workbook()
        for record in self:
            final_data = []
            line_data = []
            worksheet = workbook.add_sheet('Report Summary Card', cell_overwrite_ok=True)
            final_data.append(header_name)
            for z in record.line_ids:
                line_data = [
                             str(z.lot_id.name),
                             str(z.name),
                             z.qty_start,
                             z.qty_in,
                             z.qty_out,
                             z.qty_balance,
                             str(z.product_uom_id.name),
                             ]
                final_data.append(line_data)

            for row in range(0, len(final_data)):
                for col in range(0, len(final_data[row])):
                    value = final_data[row][col]
                    worksheet.write(row, col, value)

        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        self.name = "%s%s" % ("Report Summary Card", '.xls')
        self.export_data = base64.b64encode(output.getvalue())
        output.close()


class stock_summary_line(models.Model):
    _name 		= "vit.stock_summary_line"
    _order 		= "product_id"

    name			    = fields.Char("Description")
    stock_summary_id	= fields.Many2one('vit.stock_summary', 'Stock Card')
    product_id	        = fields.Many2one('product.product', 'Product')
    product_uom_id      = fields.Many2one('uom.uom', 'UoM')
    lot_id		        = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    stock_move_id	    = fields.Many2one('stock.move', 'Stock Move')
    expired_date	    = fields.Datetime(string='ED',store=True)
    qty_available       = fields.Float("On Hand all locations")
    qty_start		    = fields.Float("Start")
    qty_in	        	= fields.Float("Qty In")
    qty_out		        = fields.Float("Qty Out")
    qty_balance	        = fields.Float("Balance")