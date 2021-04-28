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

SC_STATES =[('draft','Draft'),('open','Open'), ('done','Done')]


class stock_card(models.Model):
    _name 		= "vit.stock_card"
    _rec_name 	= "product_id"

    @api.multi
    def unlink(self):
        for stock in self:
            if stock.state != 'draft' :
                raise UserError(_('Data yang bisa dihapus hanya yg berstatus draft'))
        return super(stock_card, self).unlink()

    ref 			= fields.Char("Number", default="/")
    date_start		= fields.Date("Date Start", required=True, default=fields.Date.today() )
    date_end		= fields.Date("Date End", required=True, default=fields.Date.today() )
    location_id		= fields.Many2one('stock.location', 'Location', required=True)
    product_id		= fields.Many2one('product.product', 'Product', required=True)
    breakdown_sn	= fields.Boolean("Per Serial Number?")
    lot_id			= fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    expired_date    = fields.Datetime(string="Expired Date", type="date",)
    # expired_date	= fields.Datetime(string="Expired Date", type="date", related='lot_id.life_date')
    line_ids		= fields.One2many('vit.stock_card_line','stock_card_id','Details', ondelete="cascade")
    state			= fields.Selection(SC_STATES,'Status',readonly=True,required=True, default="draft")
    user_id			= fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)
    name            = fields.Char('File Name', readonly=True)
    name_txt_file   = fields.Char('File Name', readonly=True)
    export_data     = fields.Binary("Export File")
    export_data_txt = fields.Binary("Export File")


    @api.multi
    def action_calculate(self):
        stock_move = self.env['stock.move']
        stock_card_line = self.env['vit.stock_card_line']
        product = self.env['product.product']

        for sc in self:
            location = sc.location_id.id
            locations = sc.env['stock.location'].search([('id', 'child_of', [location])])
            ids_location = tuple(locations.ids)
            mylist_loc_int = ids_location
            obj1 = str(ids_location).replace(',)',')')

            # kosongkan stock_card_line
            # cari stock move product_id dan location_id, start_date to end_date
            # insert into stock_card_line
            # jika keluar dari location (source_id) maka isi ke qty_out
            # jika masu ke location (dest_id) maka isi ke qty_in
            # hitung qty_balance = qty_start + qty_in - qty_out
            # start balance dihitung dari total qty stock move sebelum start_date
            cr=self.env.cr
            cr.execute("delete from vit_stock_card_line where stock_card_id=%s" % sc.id)

            qty_start = 0.0
            qty_balance = 0.0
            qty_in = 0.0
            qty_out = 0.0
            product_uom = False
            lot_id = False

            ##############################################################
            ### cari stock moves milik lot_id atau milik product_id
            ##############################################################
            if sc.breakdown_sn:
                lot_id = sc.lot_id
                sql2 = "select move_id from stock_move_line where lot_id = %s" % (lot_id.id)
            else:
                sql2 = "select move_id from stock_move_line where product_id = %s" % ( sc.product_id.id)

            cr.execute(sql2)
            res = cr.fetchall()

            move_ids = []
            move_ids_int = []
            if res and res[0]!= None:
                for move in res:
                    if str(move[0]) != 'None':
                        move_ids.append(str(move[0]))
                        move_ids_int.append(move[0])

            if move_ids:
                move_string = ','.join(x for x in move_ids)
                # move_string = "(" + "".join( [str(x) for x in move_ids] ) + ")"
                ##############################################################
                ## beginning balance in
                ##############################################################
                # sql = "select sum(product_uom_qty) from stock_move where product_id=%s " \
                #       "and date < '%s 24:00:00' and location_dest_id in %s " \
                #       "and id in (%s) "\
                #       "and state='done'" %(
                #     self.product_id.id, self.date_start, obj1, move_string)

                sql = "select product_uom, uom.factor, sum(product_uom_qty) from stock_move left join uom_uom uom on uom.id = product_uom where product_id=%s " \
                      "and date < '%s 00:00:00' and location_dest_id = %s " \
                      "and stock_move.id in (%s) "\
                      "and state='done' group by product_uom, uom.factor" %(
                    sc.product_id.id, sc.date_start, location, move_string)

                cr.execute(sql)
                res = cr.fetchall()
                qty_start = 0
                for x in res:
                    qty_start = qty_start + x[2]/x[1]

                ##############################################################
                ## beginning balance out
                ##############################################################
                sql = "select product_uom, uom.factor, sum(product_uom_qty) from stock_move left join uom_uom uom on uom.id = product_uom " \
                      "where product_id=%s " \
                      "and date < '%s 00:00:00' " \
                      "and location_id = %s " \
                      "and stock_move.id in (%s) "\
                      "and state='done' group by product_uom, uom.factor" %(
                sc.product_id.id, sc.date_start, location, move_string )

                # sql = "select sum(product_uom_qty) from stock_move " \
                #           "where product_id=%s " \
                #           "and date < '%s 24:00:00' " \
                #           "and location_id in %s " \
                #           "and id in (%s) "\
                #           "and state='done'" %(
                #     self.product_id.id, self.date_start, obj1, move_string )
                cr.execute(sql)
                res = cr.fetchall()

                # qty_start = 0
                for x in res:
                    qty_start = qty_start - x[2]/x[1]

            ## product uom
            prod = self.product_id
            product_uom = prod.uom_id


            data = {
                "stock_card_id" : sc.id,
                "date"          : False,
                "qty_start"     : False,
                "qty_in"        : False,
                "qty_out"       : False,
                "qty_balance"   : qty_start,    
                "product_uom_id": product_uom.id,   
            }
            stock_card_line.create(data)

            ##############################################################
            ## mutasi
            ##############################################################
            sm_ids = stock_move.search(['|',
                ('location_dest_id','=',location),
                ('location_id','=',location),
                ('product_id', 	'=' , sc.product_id.id),
                ('date', 		'>=', sc.date_start),
                ('date', 		'<=', sc.date_end),
                ('state',		'=',  'done'),
                ('id',			'in', move_ids_int)
            ], order='date asc')

            for sm in sm_ids:

                qty_in = 0.0
                qty_out = 0.0

                #uom conversion factor
                if product_uom.id != sm.product_uom.id:
                    factor =  product_uom.factor / sm.product_uom.factor
                    # factor = 1.0
                else:
                    factor = 1.0

                if sm.location_dest_id.id == location:#incoming, dest = location
                    qty_in = sm.product_uom_qty * factor
                elif sm.location_id.id == location:#outgoing, source = location
                    qty_out = sm.product_uom_qty * factor

                qty_balance = qty_start + qty_in - qty_out


                name = sm.name if sm.name!=prod.display_name else ""
                partner_name = sm.partner_id.name if sm.partner_id else ""
                notes = sm.picking_id.note or ""
                po_no = sm.group_id.name if sm.group_id else ""
                origin = sm.origin or ""
                finish_product = ""

                # if "MO" in origin:
                #     mrp = self.env['mrp.production']
                #     mo_id = mrp.search([("name","=",str(origin))],limit=1)
                #     # pdb.set_trace()
                #     for x in mo_id:
                #         if x.name == origin:
                #             finish_product = "%s:%s"%(x.product_id.name,x.batch_number) if mo else ""
                if "MO" in origin:
                    mrp = self.env['mrp.production']
                    mo_id = mrp.search([("name","=",origin)],limit=1)
                    # mo = mrp.browse(mo_id)
                    # di odoo 10 ga ada batch_number
                    # finish_product = "%s:%s"%(mo[0].product_id.name,mo[0].batch_number) if mo else ""
                    finish_product = "%s"%(mo_id.product_id.name) if mo_id else ""

                final_name = name
                name += ' ' + finish_product if finish_product else ''
                name += ' ' + partner_name if partner_name else ''
                name += ' ' + notes if notes else ''
                name += ' ' + origin if origin else ''


                data = {
                "stock_card_id" : self.id,
                "move_id"       : sm.id,
                "picking_id"    : sm.picking_id.id,
                "lot_id"        : self.find_lot_id(cr, sm.id ),
                "date"          : sm.date,
                "qty_start"     : qty_start,
                "qty_in"        : qty_in,
                "qty_out"       : qty_out,
                "qty_balance"   : qty_balance,
                "product_uom_id": product_uom.id,
                "name"          : final_name,
                }
                stock_card_line.create(data)
                qty_start = qty_balance
        return

    def action_draft(self):
        #set to "draft" state
        return self.write({'state':SC_STATES[0][0]})

    def action_confirm(self):
        #set to "confirmed" state
        return self.write({'state':SC_STATES[1][0]})

    def action_done(self):
        #set to "done" state
        return self.write({'state':SC_STATES[2][0]})

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('vit.stock_card')
        new_id = super(stock_card, self).create(vals)
        return new_id

    def find_lot_id(self, cr, move_id):

        lot_id = False

        sql = "select distinct(lot_id) from stock_move_line where move_id=%s"

        cr.execute(sql, (move_id,))
        res = cr.fetchall()

        if res and res[0]!= None:
            lot_id = res[0]

        return lot_id


    def cron_action_calculate(self):
        stock_card_exist = self.search([('state','in',('done','open'))])
        for card in stock_card_exist :
            date_now = date.today()
            card.update({'date_end':date_now})
            card.action_calculate()
            info = 'Stock Card '+str(card.ref)+' Updated..'
            # print info

    @api.multi
    def export(self):
        header_name = ['Date',
            'Picking',
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
            worksheet = workbook.add_sheet('Report Stock Card', cell_overwrite_ok=True)
            final_data.append(header_name)
            for z in record.line_ids:
                line_data = [
                             str(z.date),
                             str(z.picking_id.name),
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
        self.name = "%s%s" % ("Report Stock Card", '.xls')
        self.export_data = base64.b64encode(output.getvalue())
        output.close()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'hr.report.pajak.xlsx',
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'res_id': self.id,
    #         'views': [(False, 'form')],
    #         'target': 'new',
    #     }

    # @api.multi
    # def action_done(self):
    #     return {
    #         'type': 'ir.actions.act_window_close'
    #     }

class stock_card_line(models.Model):
    _name 			= "vit.stock_card_line"

    name            = fields.Char("Description")
    stock_card_id   = fields.Many2one('vit.stock_card_id', 'Stock Card')
    move_id         = fields.Many2one('stock.move', 'Stock Move')
    picking_id      = fields.Many2one('stock.picking', 'Picking')
    lot_id          = fields.Many2one('stock.production.lot', 'Lot/Serial Number')
    date            = fields.Date("Date")
    qty_start       = fields.Float("Start")
    qty_in          = fields.Float("Qty In")
    qty_out         = fields.Float("Qty Out")
    qty_balance     = fields.Float("Balance")
    product_uom_id  = fields.Many2one('uom.uom', 'UoM')