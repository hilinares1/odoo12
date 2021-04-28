from odoo import fields, models, api, _
from odoo.exceptions import UserError

# SC_STATES = [('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')]


class stock_card(models.Model):
    _name = "fal.stock.card"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Stock Card"

    name = fields.Char("Number", default="/")
    date_start = fields.Date("Date Start", required=True, track_visibility='onchange', default=fields.Date.today())
    date_end = fields.Date("Date End", required=True, track_visibility='onchange', default=fields.Date.today())
    location_id = fields.Many2one('stock.location', 'Location', track_visibility='onchange', required=True)
    product_id = fields.Many2one('product.product', 'Product', track_visibility='onchange', required=True)
    lot_id = fields.Many2one('stock.production.lot', 'Serial Number')
    expired_date = fields.Date(string="Expired Date")
    line_ids = fields.One2many('fal.stock.card.line', 'stock_card_id', 'Details', ondelete="cascade")
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'Open'),
        ('done', 'Done')], 'Status', readonly=True,
        required=True, default="draft")
    user_id = fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise UserError(_('In order to delete a stock card, \
                    you must cancel it first.'))
        return super(stock_card, self).unlink()

    @api.multi
    def action_calculate(self):
        # empty stock_card_line
        # find stock move product_id and location_id, start_date to end_date
        # insert into stock_card_line
        # if out from location (source_id) then fill to qty_out
        # if exist on location (dest_id) then fill to qty_in
        # count qty_balance = qty_start + qty_in - qty_out
        # start balance counted from sum qty stock move before start_date

        stock_move = self.env['stock.move']
        stock_card_line = self.env['fal.stock.card.line']

        for sc in self:
            self.env.cr.execute(
                "delete from fal_stock_card_line \
                where stock_card_id=%s" % sc.id
            )

            qty_start = 0.0
            qty_balance = 0.0
            qty_in = 0.0
            qty_out = 0.0
            product_uom = False

            sql2 = "select move_id from \
                stock_move_line where product_id = %s" % (sc.product_id.id)
            self.env.cr.execute(sql2)
            res = self.env.cr.fetchall()
            move_ids = []
            if res and res[0] != 'None':
                for move in res:
                    move_ids.append(move[0])
            else:
                raise UserError(_('No Data for this Product!'))

            # beginning balance in
            sql = "select sum(product_uom_qty) from stock_move where product_id=%s \
                  and date < '%s' and location_dest_id=%s \
                  and id IN %s \
                  and state='done'" % (
                sc.product_id.id, sc.date_start,
                sc.location_id.id,
                '(%s)' % ', '.join(map(repr, tuple(move_ids))),)

            self.env.cr.execute(sql)
            res = self.env.cr.fetchone()

            if res and res[0]:
                qty_start = res[0]

            # beginning balance out
            sql_prod_qty_out = "select sum(product_uom_qty) from stock_move \
                where product_id=%s and date < '%s' and \
                location_id=%s and state='done'" % (
                sc.product_id.id, sc.date_start, sc.location_id.id)

            self.env.cr.execute(sql_prod_qty_out)
            res_prod_qty_out = self.env.cr.fetchone()

            if res_prod_qty_out and res_prod_qty_out[0]:
                qty_start = qty_start - res_prod_qty_out[0]

            # product uom
            # import pdb;pdb.set_trace()
            prod = sc.product_id
            product_uom = prod.uom_id

            data = {
                "stock_card_id": sc.id,
                "name": 'Beginning Data',
                "date": False,
                "qty_start": qty_start,
                "qty_in": qty_in,
                "qty_out": qty_out,
                "qty_balance": qty_start,
                "product_uom_id": product_uom.id,
            }
            stock_card_line.create(data)

            # mutasi
            sm_ids = stock_move.search([
                '|',
                ('location_dest_id', '=', sc.location_id.id),
                ('location_id', '=', sc.location_id.id),
                ('product_id', '=', sc.product_id.id),
                ('date', '>=', sc.date_start),
                ('date', '<=', sc.date_end),
                ('state', '=', 'done'),
                ('id', 'in', move_ids)
            ], order='date asc')

            for sm in sm_ids:

                qty_in = 0.0
                qty_out = 0.0

                if product_uom.id != sm.product_uom.id:
                    factor = product_uom.factor / sm.product_uom.factor
                else:
                    factor = 1.0

                # incoming, dest = location
                if sm.location_dest_id == sc.location_id:
                    qty_in = sm.product_uom_qty * factor
                # outgoing, source = location
                elif sm.location_id == sc.location_id:
                    qty_out = sm.product_uom_qty * factor

                qty_balance = qty_start + qty_in - qty_out

                name = sm.name if sm.name != prod.display_name else ""
                partner_name = sm.partner_id.name if sm.partner_id else ""
                notes = sm.picking_id.note or ""
                po_no = sm.group_id.name if sm.group_id else ""
                origin = sm.origin or ""
                finish_product = ""

                if "MO" in origin:
                    mrp = self.env['mrp.production']
                    mo = mrp.search([("name", "=", origin)])
                    finish_product = "%s" % (
                        mo[0].product_id.name,
                    ) if mo else ""

                data = {
                    "stock_card_id": sc.id,
                    "move_id": sm.id,
                    "picking_id": sm.picking_id.id,
                    "date": sm.date,
                    "qty_start": qty_start,
                    "qty_in": qty_in,
                    "qty_out": qty_out,
                    "qty_balance": qty_balance,
                    "product_uom_id": product_uom.id,
                    "name": "%s/ %s/ %s/ %s/ %s/ %s" % (
                        name, finish_product,
                        partner_name, po_no, notes, origin),
                }
                stock_card_line.create(data)
                qty_start = qty_balance
        return

    def action_draft(self):
        # set to "draft" state
        return self.write(
            {'state': 'draft'}
        )

    def action_confirm(self):
        # set to "confirmed" state
        return self.write(
            {'state': 'open'}
        )

    def action_done(self):
        # set to "done" state
        return self.write(
            {'state': 'done'}
        )

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            seq_obj = self.env['ir.sequence']
            vals['name'] = seq_obj.next_by_code(
                'fal.stock.card') or '/'
        new_id = super(stock_card, self).create(vals)
        return new_id


class stock_card_line(models.Model):
    _name = "fal.stock.card.line"
    _description = "Stock Card Line"

    name = fields.Char("Description")
    stock_card_id = fields.Many2one('fal.stock.card', 'Stock Card')
    move_id = fields.Many2one('stock.move', 'Stock Move')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    date = fields.Date("Date")
    qty_start = fields.Float("Start")
    qty_in = fields.Float("Qty In")
    qty_out = fields.Float("Qty Out")
    qty_balance = fields.Float("Balance")
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
