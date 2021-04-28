from odoo import fields, models, api, _
from odoo.exceptions import UserError


class stock_summary(models.Model):
    _name = "fal.stock.summary"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Summary Card"

    name = fields.Char("Number", default="/")
    date_start = fields.Date("Date Start", required=True, track_visibility='onchange', default=fields.Date.today())
    date_end = fields.Date("Date End", required=True, track_visibility='onchange', default=fields.Date.today())
    location_id = fields.Many2one('stock.location', 'Location', required=True, track_visibility='onchange')
    line_ids = fields.One2many('fal.stock.summary.line', 'stock_summary_id', 'Details', ondelete="cascade")
    breakdown_sn = fields.Boolean("Breakdown Serial Number?")
    state = fields.Selection([
        ('draft', 'Draft'), ('open', 'Open'),
        ('done', 'Done'), ('post', 'Post')], 'Status',
        readonly=True, required=True, default="draft")
    user_id = fields.Many2one('res.users', 'Created', default=lambda self: self.env.user)
    move_id = fields.Many2one('account.move', string="Journal Entries")
    journal_id = fields.Many2one('account.journal', string='Journal')
    stock_valuation_acc = fields.Many2one('account.account', string='Stock Valuation Account')
    expense_acc = fields.Many2one('account.account', string='Expense Account')

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise UserError(_('In order to delete a stock summary, you must cancel it first.'))
        return super(stock_summary, self).unlink()

    @api.multi
    def post_journal(self):
        created_moves = self.env['account.move']
        line_list = []
        for line in self.line_ids:
            name = line.stock_summary_id.name + " - " + line.product_id.name
            product = line.product_id
            company_currency = self.env.user.company_id.currency_id
            qty_in_val = line.qty_in * line.product_id.standard_price
            qty_out_val = line.qty_out * line.product_id.standard_price
            if qty_out_val != qty_in_val:
                diff_val = qty_in_val - qty_out_val
            else:
                diff_val = 0.0

            # Credit
            if qty_out_val > 0.0:
                credit_1 = 0.0
                debit_1 = abs(qty_out_val)
                diff_amount = abs(qty_out_val)
            else:
                credit_1 = abs(qty_out_val)
                debit_1 = 0.0
                diff_amount = -1 * abs(qty_out_val)
            move_line_1 = {
                'name': name,
                'account_id': line.stock_summary_id.expense_acc.id,
                'credit': credit_1,
                'debit': debit_1,
                'journal_id': line.stock_summary_id.journal_id.id,
                'currency_id': company_currency.id or False,
                'amount_currency': diff_amount,
                'product_id': product.id,
                'product_uom_id': 1
            }
            line_list.append((0, 0, move_line_1))
            # Debit
            if qty_in_val > 0.0:
                credit_2 = abs(qty_in_val)
                debit_2 = 0.0
                diff_amount = -1 * abs(qty_in_val)
            else:
                credit_2 = 0.0
                debit_2 = abs(qty_in_val)
                diff_amount = abs(qty_in_val)
            move_line_2 = {
                'name': name,
                'account_id': line.stock_summary_id.stock_valuation_acc.id,
                'credit': credit_2,
                'debit': debit_2,
                'journal_id': line.stock_summary_id.journal_id.id,
                'currency_id': company_currency.id or False,
                'amount_currency': diff_amount,
                'product_id': product.id,
                'product_uom_id': 1
            }
            line_list.append((0, 0, move_line_2))
            if diff_val:
                # Diff Credit and Debit
                if diff_val > 0.0:
                    credit_3 = 0.0
                    debit_3 = abs(diff_val)
                    diff_amount = abs(diff_val)
                else:
                    credit_3 = abs(diff_val)
                    debit_3 = 0.0
                    diff_amount = -1 * abs(diff_val)
                move_line_3 = {
                    'name': name,
                    'account_id': line.stock_summary_id.stock_valuation_acc.id,
                    'credit': credit_3,
                    'debit': debit_3,
                    'journal_id': line.stock_summary_id.journal_id.id,
                    'currency_id': company_currency.id or False,
                    'amount_currency': diff_amount,
                    'product_id': product.id,
                    'product_uom_id': 1
                }
                line_list.append((0, 0, move_line_3))
        move_vals = {
            'ref': line.stock_summary_id.name,
            'date': self.date_end or False,
            'journal_id': line.stock_summary_id.journal_id.id,
            'line_ids': line_list,
        }

        move = created_moves.create(move_vals)
        self.write({
            'move_id': move.id,
            'state': 'post',
        })

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

        stock_summary_line = self.env['fal.stock.summary.line']

        for sc in self:
            self.env.cr.execute(
                "delete from fal_stock_summary_line \
                where stock_summary_id=%s" % sc.id)
            self.beginning_lines_nosn(stock_summary_line, sc)
            self.mutasi_lines_nosn(stock_summary_line, sc)
            self.update_balance(sc)
            self.update_other_info(sc)
        return

    def update_other_info(self, sc):
        # set Other Info Data
        line = sc.line_ids
        if line:
            line_vals = line[0]
            categ = line_vals.product_id.categ_id
            if categ:
                journal_id = categ.property_stock_journal.id
                valuation_acc = categ.property_stock_valuation_account_id.id
                expense_acc = categ.property_account_expense_categ_id.id
                return self.write(
                    {
                        'journal_id': journal_id,
                        'stock_valuation_acc': valuation_acc,
                        'expense_acc': expense_acc
                    })
            else:
                return self.write(
                    {
                        'journal_id': False,
                        'stock_valuation_acc': False,
                        'expense_acc': False
                    })

    def beginning_lines_nosn(self, stock_summary_line, sc):
        # date = "date < (select date + INTERVAL '1 day' \
        # from stock_move as m where location_dest_id = %s \
        # and date between '%s 00:00:00' \
        # and '%s 00:00:00' and state = 'done' \
        # order by date asc limit 1)" % (
        #     sc.location_id.id, sc.date_start, sc.date_end
        # )
        date = "date >= '%s' and \
            date <= '%s'" % (sc.date_start, sc.date_end)

        line_type = "beg"
        self.process_lines_nosn(line_type, date, stock_summary_line, sc)

    def mutasi_lines_nosn(self, stock_summary_line, sc):
        date = "date >= '%s 00:00:01' and \
            date <= '%s 24:00:00'" % (sc.date_start, sc.date_end)
        line_type = "mut"
        self.process_lines_nosn(line_type, date, stock_summary_line, sc)

    def process_lines_nosn(self, line_type, date, stock_summary_line, sc):

        sql = "select product_id,\
            product_uom,\
            sum(product_uom_qty) \
            from stock_move as m \
            where %s and %s = %s \
            and state = 'done' \
            group by product_id,product_uom \
            order by product_id"

        # incoming
        self.env.cr.execute(sql % (
            date, "location_dest_id", sc.location_id.id))

        res = self.env.cr.fetchall()
        if not res or res[0] == 'None':
            pass

        qty_start = 0.0

        if line_type == "beg":
            for beg in res:

                # calculate qty_start
                sql2 = "select move_id from \
                    stock_move_line where product_id = %s" % (beg[0])
                self.env.cr.execute(sql2)
                res = self.env.cr.fetchall()
                move_ids = []
                if res and res[0] != 'None':
                    for move in res:
                        move_ids.append(move[0])
                else:
                    raise UserError(_('No Data for this Product!'))

                # beginning balance in
                sql_prod_qty_in = "select sum(product_uom_qty) from stock_move where product_id=%s \
                      and date < '%s' and location_dest_id=%s \
                      and id IN %s \
                      and state='done'" % (
                    beg[0], sc.date_start,
                    sc.location_id.id,
                    '(%s)' % ', '.join(map(repr, tuple(move_ids))),)

                self.env.cr.execute(sql_prod_qty_in)
                res = self.env.cr.fetchone()

                if res and res[0]:
                    qty_start = res[0]

                # beginning balance out
                sql_prod_qty_out = "select sum(product_uom_qty) from stock_move \
                    where product_id=%s and date < '%s' and \
                    location_id=%s and state='done'" % (
                    beg[0], sc.date_start, sc.location_id.id)

                self.env.cr.execute(sql_prod_qty_out)
                res_prod_qty_out = self.env.cr.fetchone()

                if res_prod_qty_out and res_prod_qty_out[0]:
                    qty_start = qty_start - res_prod_qty_out[0]

                product_id = beg[0]
                sm_uom_id = beg[1]
                qty = beg[2]
                qty, product_uom_id = self.convert_uom_qty(
                    product_id, sm_uom_id, qty)
                data = {
                    "stock_summary_id": sc.id,
                    "product_id": product_id,
                    "product_uom_id": product_uom_id,
                    "qty_start": qty_start,
                    "qty_in": 0,
                    "qty_out": 0,
                    "qty_balance": 0,
                }
                stock_summary_line.create(data)
        else:
            for incoming in res:
                product_id = incoming[0]
                sm_uom_id = incoming[1]
                qty = incoming[2]
                qty, product_uom_id = self.convert_uom_qty(
                    product_id, sm_uom_id, qty)
                sql2 = "update fal_stock_summary_line set \
                        qty_in = %s \
                        where stock_summary_id = %s and \
                        product_id=%s" % (qty, sc.id, product_id)
                self.env.cr.execute(sql2)

        # outgoing
        self.env.cr.execute(sql % (
            date, "location_id", sc.location_id.id))

        res = self.env.cr.fetchall()
        if not res or res[0] == 'None':
            pass

        if res:
            for outgoing in res:
                product_id = outgoing[0]
                sm_uom_id = outgoing[1]
                qty3 = abs(outgoing[2])
                qty3, product_uom_id = self.convert_uom_qty(
                    product_id, sm_uom_id, qty3)

                sql2 = """update fal_stock_summary_line set \
                            qty_out = %s \
                            where stock_summary_id = %s and \
                            product_id=%s """ % (
                    qty3, sc.id, product_id)
                self.env.cr.execute(sql2)

        # balance
        sql = """update fal_stock_summary_line \
            set qty_balance = qty_start + qty_in - qty_out \
            where stock_summary_id = %s """ % (sc.id)
        self.env.cr.execute(sql)

    def convert_uom_qty(self, product_id, sm_uom_id, qty):

        product = self.env['product.product'].browse(product_id)
        uom = self.env['uom.uom'].browse(sm_uom_id)

        if uom.id != product.uom_id.id:
            factor = product.uom_id.factor / uom.factor
        else:
            factor = 1.0

        converted_qty = qty * factor

        return converted_qty, product.uom_id.id

    def update_balance(self, sc):
        sql3 = "update fal_stock_summary_line set \
            qty_balance =  coalesce( qty_start,0) + \
            coalesce(qty_in,0) - coalesce(qty_out,0) \
            where stock_summary_id = %s " % (sc.id)
        self.env.cr.execute(sql3)

    def action_draft(self):
        moves = self.env['account.move']
        for stock in self:
            if stock.move_id:
                moves += stock.move_id
        # First, set the stock summary as cancelled and detach the move ids
        self.write({'state': 'draft', 'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return True

    def action_confirm(self):
        # set to "confirmed" state
        return self.write(
            {'state': 'open'})

    def action_done(self):
        # set to "done" state
        return self.write(
            {'state': 'done'})

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fal.stock.summary') or '/'
        new_id = super(stock_summary, self).create(vals)
        return new_id


class stock_summary_line(models.Model):
    _name = "fal.stock.summary.line"
    _description = "Summary Card Line"

    name = fields.Char("Description")
    stock_summary_id = fields.Many2one('fal.stock.summary', 'Stock Card')
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_id = fields.Many2one('uom.uom', 'UoM')
    lot_id = fields.Many2one('stock.production.lot', 'Serial Number')
    expired_date = fields.Date(string="Expired Date")
    qty_start = fields.Float("Start")
    qty_in = fields.Float("Qty In")
    qty_out = fields.Float("Qty Out")
    qty_balance = fields.Float("Balance")
