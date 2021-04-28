from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import math
from itertools import groupby
from operator import itemgetter
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class FalInvoiceTerm(models.Model):
    _name = 'fal.invoice.term'
    _description = 'Invoice Term'
    _inherit = ['mail.thread']

    fal_template_id = fields.Many2one('fal.invoice.term', string="Rules Template", domain=[('is_template', '=', True)])
    fal_invoice_rules = fields.Selection([
        ('milestone', 'Invoice Milestone'),
        ('subscription', 'Subscription'),
    ], string='Rules', required=True, default='milestone')
    is_template = fields.Boolean(string="Is template")
    fal_invoice_rules_type = fields.Selection([
        ('percentage', 'By percentage'),
        ('amount', 'By Exact Amount'),
    ], string="Rules Type", required=True, default='percentage')
    total_amount = fields.Float(
        compute="_compute_total_amount",
        string="Total Amount", store=1)
    active = fields.Boolean('Active', default=1)
    name = fields.Char('Name', size=64, required=1)
    sequence = fields.Integer('Sequence', default=10)
    type = fields.Selection(
        [
            ('date', 'By Date'),
        ],
        'Type', default='date', required=1)
    fal_invoice_term_line_ids = fields.One2many(
        'fal.invoice.term.line', 'fal_invoice_term_id',
        track_visibility="onchange")
    total_percentage = fields.Float(
        compute="_compute_total_percentage",
        string="Total Percentage(%)", store=1)
    recurring_rule_type = fields.Selection([
        ('daily', 'Day(s)'), ('weekly', 'Week(s)'),
        ('monthly', 'Month(s)'), ('yearly', 'Year(s)'), ],
        string='Recurrence', required=True,
        help="Invoice automatically repeat at specified interval",
        default='monthly')
    recurring_interval = fields.Integer(
        string="Repeat Every", help="Repeat every (Days/Week/Month/Year)",
        required=True, default=1, track_visibility='onchange')
    recurring_rule_boundary = fields.Selection([
        ('unlimited', 'Forever'),
        ('limited', 'Fixed')
    ], string='Duration', default='unlimited')
    recurring_rule_count = fields.Integer(string="End After", default=1)
    date_start = fields.Date(string='Start Date', default=fields.Date.today)
    product_id = fields.Many2one('product.product', string='Product')
    sale_order_ids = fields.Many2many('sale.order', string='Sale Order', compute="_get_related_sale_order")

    def _get_related_sale_order(self):
        for rule in self:
            so = self.env['sale.order'].search([('fal_invoice_term_id', '=', rule.id)])
            rule.sale_order_ids = [(6, 0, so.ids)]

    @api.onchange('fal_template_id')
    def _onchange_template(self):
        if self.fal_template_id:
            self.fal_invoice_term_line_ids = False
            self.fal_invoice_rules = self.fal_template_id.fal_invoice_rules
            self.fal_invoice_rules_type = self.fal_template_id.fal_invoice_rules_type
            self.recurring_rule_type = self.fal_template_id.recurring_rule_type
            self.recurring_interval = self.fal_template_id.recurring_interval
            self.recurring_rule_boundary = self.fal_template_id.recurring_rule_boundary
            self.recurring_rule_count = self.fal_template_id.recurring_rule_count
            self.product_id = self.fal_template_id.product_id.id

            ruleline = []
            for line in self.fal_template_id.fal_invoice_term_line_ids:
                ruleline.append((0, 0, {
                    'percentage': line.percentage,
                    'fal_invoice_rules': line.fal_invoice_rules,
                    'fal_invoice_rules_type': line.fal_invoice_rules_type,
                    'date': line.date,
                    'sequence': line.sequence,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'description': line.description,
                    'is_final': line.is_final,
                }))
            self.fal_invoice_term_line_ids = ruleline

    @api.one
    @api.constrains('total_percentage')
    def _check_total_percentage(self):
        ctx = dict(self._context)
        if not ctx.get('from_template'):
            if self.fal_invoice_rules == 'milestone':
                if self.fal_invoice_rules_type == 'percentage':
                    if self.total_percentage > 100:
                        raise UserError(_(
                            "Total Percentage cannot be greater than 100"))
                    if self.total_percentage < 100:
                        raise UserError(_("Total Percentage cannot be lower than 100"))

    @api.multi
    @api.depends(
        'fal_invoice_term_line_ids',
        'fal_invoice_term_line_ids.percentage')
    def _compute_total_percentage(self):
        for invoiceTerm in self:
            temp = 0
            for line in invoiceTerm.fal_invoice_term_line_ids:
                temp += line.percentage
            invoiceTerm.total_percentage = temp

    @api.multi
    @api.depends(
        'fal_invoice_term_line_ids',
        'fal_invoice_term_line_ids.amount')
    def _compute_total_amount(self):
        for invoiceTerm in self:
            temp = 0
            for line in invoiceTerm.fal_invoice_term_line_ids:
                temp += line.amount
            invoiceTerm.total_amount = temp

    @api.onchange('fal_invoice_rules', 'recurring_rule_count', 'recurring_rule_type', 'recurring_interval', 'date_start')
    def onchange_type(self):
        temp = []
        if self.fal_invoice_rules == 'subscription':
            self.fal_invoice_term_line_ids = False
            percent = 100
            int_frequency = percent / self.recurring_rule_count
            int_percent = math.trunc(int_frequency)
            seq = 0
            val_order_date = self.date_start
            int_days = self.recurring_interval
            var_date = val_order_date
            while percent != 0:
                seq += 1
                if percent >= (int_percent * 2):
                    val_percent = int_percent
                    percent = percent - int_percent
                    is_final = False
                else:
                    val_percent = percent
                    percent = percent - percent
                    is_final = True

                if self.recurring_rule_type == 'daily':
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            timedelta(days=int_days)
                        var_date = var_date + timedelta(days=int_days)
                    else:
                        var_date = var_date + timedelta(days=int_days)
                elif self.recurring_rule_type == 'weekly':
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            relativedelta(weeks=int_days)
                        var_date = var_date + relativedelta(weeks=int_days)
                    else:
                        var_date = var_date + relativedelta(weeks=int_days)
                elif self.recurring_rule_type == 'monthly':
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            relativedelta(months=int_days)
                        var_date = var_date + relativedelta(months=int_days)
                    else:
                        var_date = var_date + relativedelta(months=int_days)
                elif self.recurring_rule_type == 'yearly':
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            relativedelta(years=int_days)
                        var_date = var_date + relativedelta(years=int_days)
                    else:
                        var_date = var_date + relativedelta(years=int_days)

                temp.append((0, 0, {
                    'percentage': val_percent,
                    'fal_invoice_rules': self.fal_invoice_rules,
                    'fal_invoice_rules_type': self.fal_invoice_rules_type,
                    'date': val_order_date,
                    'sequence': seq,
                    'product_id': self.product_id.id,
                    'name': self.product_id.name,
                    'description': "%s Term %s" % (self.product_id.name, seq),
                    'is_final': is_final,
                }))
        self.fal_invoice_term_line_ids = temp

    def take_template(self):
        for term in self:
            invoice_rules = term.with_context({'from_template': True}).copy(default={'is_template': False})
            for line in term.fal_invoice_term_line_ids:
                line.with_context({'from_template': True}).copy(default={'fal_invoice_term_id': invoice_rules.id})

            return {
                'name': _('Invoice Rules'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fal.invoice.term',
                'type': 'ir.actions.act_window',
                'res_id': invoice_rules.id,
                'target': 'current'
            }

# end of FalInvoiceTerm()


class FalInvoiceTermLine(models.Model):
    _name = 'fal.invoice.term.line'
    _order = 'date, sequence, id'
    _inherit = ['mail.thread']

    is_template = fields.Boolean(string="Is template", related="fal_invoice_term_id.is_template")
    fal_invoice_rules = fields.Selection([
        ('milestone', 'Invoice Milestone'),
        ('subscription', 'Subscription'),
    ], string='Rules')
    fal_invoice_rules_type = fields.Selection([
        ('percentage', 'By percentage'),
        ('amount', 'By Exact Amount'),
    ], string="Rules Type")
    amount = fields.Float(
        'Exact Amount', track_visibility="onchange")

    # It can connect to Invoice Term
    parent_id = fields.Many2one('fal.invoice.term.line')
    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Term')
    # Or to Sale Order, it may only has order id
    fal_order_id = fields.Many2one("sale.order", string="Order Id")
    # Or also a line
    fal_sale_order_id = fields.Many2one(
        "sale.order", related="fal_sale_order_line_id.order_id",
        string="Sale Order", store=True)
    fal_sale_order_line_id = fields.Many2one(
        "sale.order.line", string="Order Line")
    invoice_term_type = fields.Selection(
        'Invoice Term Type', related='fal_invoice_term_id.type',
        track_visibility="onchange")
    sequence = fields.Integer('Sequence', default=10)

    product_id = fields.Many2one(
        'product.product', 'Product', track_visibility="onchange")
    name = fields.Char(string='Description Product', related="product_id.name")
    description = fields.Char(string='Description Line')
    percentage = fields.Float(
        'Percentage (%)', track_visibility="onchange", required="1")
    date = fields.Date('Invoice Date', track_visibility="onchange")
    is_final = fields.Boolean(
        'Is Final Term', compute='_compute_is_final',
        track_visibility="onchange")

    invoice_forecast_date = fields.Date(
        "Invoice Forecast Date", track_visibility="onchange")
    invoice_id = fields.Many2one(
        "account.invoice", string="Invoice", copy=False)
    total_amount = fields.Float(string="Total Amount", compute='_compute_total_amount')

    @api.multi
    def write(self, vals):
        res = super(FalInvoiceTermLine, self).write(vals)
        for term in self:
            if 'date' or 'invoice_forecast_date' in vals:
                term_line_ids = self.search([
                    ('parent_id', '=', term.id),
                    ('invoice_id', '=', False),
                ])
                for termline in term_line_ids:
                    termline.sudo().write({
                        'date': term.date,
                        'invoice_forecast_date': term.invoice_forecast_date,
                    })
        return res

    @api.depends('percentage', 'fal_sale_order_line_id', 'fal_sale_order_line_id.price_unit', 'fal_sale_order_line_id.product_uom_qty')
    def _compute_total_amount(self):
        for sale in self:
            sale.total_amount = (sale.percentage * sale.fal_sale_order_line_id.price_subtotal) / 100

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.description = self.product_id.name

    @api.one
    @api.depends('sequence', 'date', 'fal_invoice_term_id')
    def _compute_is_final(self):
        # It either on Invoice Term / Sales order Line
        if self.fal_invoice_term_id:
            last_invoice_term = False
            # We trust odoo order to make the last sequence as Final
            for invoice_term_line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                invoice_term_line.is_final = False
                last_invoice_term = invoice_term_line
            if last_invoice_term:
                last_invoice_term.is_final = True
        elif self.fal_sale_order_line_id:
            last_invoice_term = False
            # We trust odoo order to make the last sequence as Final
            for invoice_term_line in self.fal_sale_order_line_id.fal_invoice_milestone_line_date_ids:
                invoice_term_line.is_final = False
                last_invoice_term = invoice_term_line
            if last_invoice_term:
                last_invoice_term.is_final = True

    @api.model
    def _cron_generate_invoice_order_line_by_planning_date(self):

        current_date = datetime.now()

        term_line_ids = self.search([
            ('date', '<=', current_date),
            ('fal_sale_order_line_id', '!=', False),
            ('invoice_id', '=', False),
            ('fal_sale_order_id.state', '=', 'sale'),
            ('fal_sale_order_id.fal_milestone_by_cron', '=', True)])

        return term_line_ids._generate_invoice_order_line_by_planning_date()

    @api.multi
    def _generate_invoice_order_line_by_planning_date(self):
        advance_wizard_obj = self.env['sale.advance.payment.inv']
        res = False
        for term_line in self:
            orderline = term_line.fal_sale_order_line_id
            order = orderline.order_id
            if term_line.fal_invoice_rules == 'subscription':
                invoice_obj = self.env['account.invoice']
                invoice_line_obj = self.env['account.invoice.line']
                vals = order.with_context(force_company=order.company_id.id, company_id=order.company_id.id)._prepare_invoice()
                inv_id = invoice_obj.create(vals)
                qty = orderline.product_uom_qty / orderline.fal_invoice_term_id.recurring_rule_count
                vals_line = orderline.with_context(force_company=order.company_id.id, company_id=order.company_id.id)._prepare_invoice_line(qty=qty)
                vals_line.update({'invoice_id': inv_id.id, 'sale_line_ids': [(6, 0, [orderline.id])]})
                invoice_line_obj.create(vals_line)
                inv_id._onchange_invoice_line_ids()
                term_line.invoice_id = inv_id.id
            else:
                if not term_line.is_final:
                    # Call Odoo downpayment Wizard function
                    wizard_vals = {
                        'advance_payment_method': 'percentage' if order.fal_invoice_term_id.fal_invoice_rules_type == 'percentage' else 'fixed',
                        'amount': term_line.percentage if order.fal_invoice_term_id.fal_invoice_rules_type == 'percentage' else term_line.amount,
                        'product_id': term_line.product_id.id,
                        'description': term_line.product_id.name

                    }
                    advPmnt = advance_wizard_obj.create(wizard_vals)
                    advPmnt.with_context({
                        'active_ids': [order.id],
                        'so_line': orderline,
                        'term_line': term_line}).fal_milestone_create_invoices()
                else:
                    # Call Odoo downpayment Wizard function
                    wizard_vals = {
                        'advance_payment_method': 'all',
                    }
                    advPmnt = advance_wizard_obj.create(wizard_vals)
                    advPmnt.with_context({
                        'active_ids': [order.id],
                        'so_line': orderline,
                        'term_line': term_line}).fal_milestone_create_invoices()

        sale_order = self.mapped('fal_sale_order_id')
        for sale in sale_order:
            _type = []
            res = {}
            for term in self.filtered(lambda a: a.fal_sale_order_id == sale):
                _type.append((term.date, term))
            for date, val in _type:
                if date in res:
                    res[date] += val
                else:
                    res[date] = val
            for key in res:
                for term_id in res[key]:
                    term_id.invoice_id.invoice_line_ids.write({'invoice_id': res[key][0].invoice_id.id})
                    if term_id != res[key][0]:
                        term_id.invoice_id.unlink()
                        term_id.write({'invoice_id': res[key][0].invoice_id.id})
                    term_id.invoice_id.write({'date_invoice': term_id.date})
        return res

    @api.multi
    def action_open_form_view(self):
        self.ensure_one()
        if self.invoice_id:
            raise UserError(_('You cannot edit invoice term line that already invoiced'))
        return{
            'name': _('Invoice Term Line'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.invoice.term.line',
            'view_id': self.env.ref('fal_invoice_milestone.fal_invoice_term_line_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    @api.multi
    def open_change_term_line(self):
        term_line_ids = self.search([
            ('parent_id', '=', self.id),
            ('invoice_id', '=', False),
            ('fal_sale_order_line_id', '!=', False),
        ])

        context = {
            'default_fal_invoice_term_line_ids': [(6, 0, term_line_ids.ids)],
            'default_date': self.date,
            'default_invoice_forecast_date': self.invoice_forecast_date,
            'default_term_line': self.id,
        }

        return {
            'name': _('Change Line'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'change.term.line.wizard',
            'view_id': self.env.ref('fal_invoice_milestone.fal_change_term_line_wizard').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }
