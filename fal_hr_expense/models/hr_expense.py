from odoo import models, fields, api, _
# import openerp.addons.decimal_precision as dp
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from decimal import *
import logging

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def _get_currency(self):
        user_obj = self.env['res.users']
        currency_obj = self.env['res.currency']
        uid = self._uid
        user = user_obj.browse(uid)

        if user.company_id:
            return user.company_id.currency_id
        else:
            return currency_obj.search([('rate', '=', 1.0)])[0]

    # Field definition ===========================

    # Amount Computation
    # Real Amount & Currency because of we don't want to use multi-currencies on expense
    fal_real_amount = fields.Float(
        string='Total Expense', digits=dp.get_precision('Product Price'))
    fal_real_currency = fields.Many2one(
        'res.currency', string='Real Currency', required=True, default=_get_currency)

    fal_accepted_amount = fields.Float(
        string='Accepted Total TTC', digits=dp.get_precision('Product Price'),
        track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)], 'reported': [('readonly', False)]})
    fal_refund_cost_price = fields.Boolean(related='product_id.fal_refund_cost_price', string='fal_refund_cost_price')

    unit_amount = fields.Float(compute='get_unit_price_fal', store=True, required=False, states={}, digits=dp.get_precision('Decimal Expense'))
    fal_withouttax_price = fields.Monetary(string='Without Tax Total', digits=dp.get_precision('Decimal Expense'), compute='get_tax_total')
    fal_total_tax = fields.Monetary(string='Total Tax', digits=dp.get_precision('Decimal Expense'), compute='get_tax_total')
    fal_withtax_price = fields.Monetary(string='WithTax Total Price', digits=dp.get_precision('Product Price'), compute='get_tax_total')

    # Budget Management
    fal_budget = fields.Monetary(compute='_get_budget', digits=dp.get_precision('Product Price'), string='Total Budget', store=True)
    fal_expense_control = fields.Char(compute='_get_expense_control', string='Expense Control', store=True)
    fal_gap = fields.Monetary(string='Gap', compute='_get_gap_amount')

    # Other Info
    fal_is_related_to_partner = fields.Boolean(related='product_id.fal_is_related_to_partner', string='Expense related to Partner')
    fal_with_partner_ids = fields.Many2many('res.partner', 'fal_hr_expense_partner_rel', 'expense_line_id', 'partner_id', string='Partners')

    fal_location = fields.Char(string='Location', readonly=True,
        states={'draft': [('readonly', False)], 'reported': [('readonly', False)]})
    fal_reason = fields.Text(string='Explanation')
    fal_reason_why = fields.Selection([
        ('customer', 'With Customer'),
        ('manager', 'With Manager'),
        ('director', 'Require Refund To Director'),
        ('employee', 'Require at Employee Charge')],
        string="Reason")

    # Security
    fal_parent_id = fields.Many2one('hr.employee', related='employee_id.parent_id', string='Parent', store=True)

    #State
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('reported', 'Submitted'),
        ('approved', 'Approved'),
        ('post', 'Waiting Payment'),
        ('done', 'Paid'),
        ('refused', 'Refused')
    ], default='draft')

    # Accounting
    fal_account_move_id = fields.Many2one('account.move', string='Journal Entry', copy=False, related="sheet_id.account_move_id")
    fal_expense_tax_line_ids = fields.One2many('account.expense.tax', 'expense_id', string='Tax Lines', readonly=True, states={'draft': [('readonly', False)]}, copy=True)

    # Attachment for Proof
    fal_is_no_proof = fields.Boolean(string='No Proof')

    # compute state
    @api.depends('sheet_id', 'sheet_id.account_move_id', 'sheet_id.state')
    def _compute_state(self):
        res = super(HrExpense, self)._compute_state()
        for expense in self:
            if expense.sheet_id.state == 'post':
                expense.state = "post"
        return res

    # Need to override this, because we need to put falinwa taxes, not odoo
    @api.multi
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.address_home_id.commercial_partner_id.id

            # source move line
            amount_currency = expense.total_amount if different_currency else False
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': taxes['total_excluded'] > 0 and taxes['total_excluded'],
                'credit': taxes['total_excluded'] < 0 and -taxes['total_excluded'],
                'amount_currency': taxes['total_excluded'] > 0 and abs(amount_currency) or -abs(amount_currency),
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount -= move_line_src['debit']
            total_amount_currency -= move_line_src['amount_currency'] or move_line_src['debit']

            # taxes move lines
            for tax in expense.fal_expense_tax_line_ids:
                price = expense.currency_id._convert(
                    tax.amount, company_currency, expense.company_id, account_date)
                amount_currency = price if different_currency else False
                move_line_tax_values = {
                    'name': tax.name,
                    'quantity': 1,
                    'debit': price > 0 and price,
                    'credit': price < 0 and -price,
                    'amount_currency': price > 0 and abs(amount_currency) or -abs(amount_currency),
                    'account_id': tax.account_id.id or move_line_src['account_id'],
                    'tax_line_id': tax.tax_id.id,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                }
                total_amount -= price
                total_amount_currency -= move_line_tax_values['amount_currency'] or price
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount > 0 and abs(amount_currency) or -abs(amount_currency),
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense

    # Automatic Unit Amount calculation ============================================
    # We search using binary search
    def search_unit_price(self, target, min_value, max_value, max_iteration, old_unit_price):
        # If iteration beyond 1000 we stop
        unit_price = (min_value + max_value) / 2.0

        # Check result by calculating guess unit price
        res = self.tax_ids.with_context(round=False).compute_all(unit_price, self.currency_id, self.quantity, product=self.product_id, partner=False)

        if res['total_included'] == target or old_unit_price == unit_price:
            return unit_price
        elif res['total_included'] > target:
            return self.search_unit_price(target, min_value,unit_price, max_iteration, unit_price)
        else:
            return self.search_unit_price(target, unit_price, max_value, max_iteration, unit_price)

    @api.depends('quantity', 'tax_ids', 'product_id', 'fal_accepted_amount')
    def get_unit_price_fal(self):
        for exp in self:
            if not exp.product_id.fal_refund_cost_price:
                # Make a first guess
                # Why this is a guess because tax calculation is not that simple in odoo, too avoid confussion we use this method instead
                tmp = exp.fal_accepted_amount
                tax_total = 0.0
                total_unit = tax_amount = 0.0
                for tax in exp.tax_ids:
                    if not tax.price_include and tax.amount_type == 'percent':
                        tax_amount += tax.amount / 100
                        tax_total = (tmp / (1 + tax_amount) * (tax_amount))
                    if tax.price_include and tax.amount_type == 'percent':
                        tax_total = 0.0
                total_unit = tmp - tax_total
                if exp.quantity != 0.0:
                    total_unit /= (exp.quantity)
                # Let's do Binary Search
                real_total_unit = exp.search_unit_price(exp.fal_accepted_amount, total_unit - 100, total_unit + 100, 0, 0)
                exp.unit_amount = real_total_unit
            else:
                exp.fal_real_currency = exp.product_id.currency_id.id
                exp.unit_amount = exp.product_id.standard_price

    @api.depends('unit_amount', 'fal_accepted_amount', 'tax_ids', 'product_id', 'quantity', 'fal_real_currency')
    def get_tax_total(self):
        for item in self:
            ttax = 0.0
            if item.tax_ids:
                for tax in item.fal_expense_tax_line_ids:
                    ttax += tax.amount
            item.fal_total_tax = ttax
            # It's just impossible mathematically to get this number, because decimal rounding, etc
            # So Just to be beautiful we will make it happen
            if item.product_id:
                item.fal_withouttax_price = item.fal_accepted_amount - item.fal_total_tax
                item.fal_withtax_price = item.fal_accepted_amount

    # Fix standard odoo method because we need to use the standard odoo field for the total amount
    # We need to pass with_context round=False to make sure that decimal is correct
    @api.depends('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def _compute_amount(self):
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            # Change Here
            taxes = expense.tax_ids.with_context(round=False).compute_all(
                expense.unit_amount, expense.currency_id, expense.quantity,
                expense.product_id, expense.employee_id.user_id.partner_id)
            # End Here
            expense.total_amount = taxes.get('total_included')

    # Budgeting ============================================
    @api.multi
    @api.depends('product_id.expense_budget', 'quantity')
    def _get_budget(self):
        for expense_line in self:
            expense_line.fal_budget = 0.0
            if expense_line.product_id:
                expense_line.fal_budget = \
                    expense_line.product_id.expense_budget * \
                    expense_line.quantity

    @api.multi
    @api.depends('product_id.expense_budget', 'quantity', 'unit_amount')
    def _get_expense_control(self):
        for expense_line in self:
            expense_line.fal_expense_control = _('No Control')
            if expense_line.product_id:
                total_budget = \
                    expense_line.product_id.expense_budget * \
                    expense_line.quantity
                if expense_line.product_id.expense_budget == 0.00:
                    expense_line.fal_expense_control = _('No Control')
                elif expense_line.unit_amount < total_budget:
                    expense_line.fal_expense_control = _('In Budget')
                elif expense_line.unit_amount == total_budget:
                    expense_line.fal_expense_control = _('Max Budget')
                else:
                    expense_line.fal_expense_control = _('Out Budget')

    @api.multi
    @api.depends('fal_real_amount', 'fal_budget', 'fal_accepted_amount')
    def _get_gap_amount(self):
        for line in self:
            if line.fal_budget:
                line.fal_gap = line.fal_budget - line.fal_accepted_amount
            else:
                line.fal_gap = 0.0

    # Put bugdet & real amount
    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(HrExpense, self)._onchange_product_id()
        product = self.product_id
        if product:
            self.fal_budget = self.product_id.expense_budget

    @api.onchange('product_id', 'quantity', 'fal_budget', 'fal_real_amount')
    def onchange_quantity(self):
        product = self.product_id
        if product and self.quantity:
            self.fal_budget = product.expense_budget * self.quantity
        if product.fal_refund_cost_price and self.quantity:
            self.fal_real_amount = product.standard_price * self.quantity

    @api.onchange('unit_amount', 'fal_budget')
    def onchange_unit_price(self):
        res = {'warning': {}}
        cur_obj = self.env['res.currency']
        warning_msgs = ''
        context = dict(self._context)

        cur_id = cur_obj.browse(context.get('currency_id', 1))
        if self.fal_budget == 0.00:
            self.fal_expense_control = _('No Control')
        elif self.unit_amount < self.fal_budget:
            self.fal_expense_control = _('In Budget')
        elif self.unit_amount == self.fal_budget:
            warning_msgs = _('This line has a budget: %s %s, \
                Budget amount is at maximum. By Confirm it you ensure that \
                you really spent this amount during your mission!') % (
                self.fal_budget, cur_id.symbol)
            self.fal_expense_control = _('Max Budget')
        else:
            warning_msgs = _('This line has a budget: %s %s, \
                You are out of budget!') % (self.fal_budget, cur_id.symbol)
            self.fal_expense_control = _('Out Budget')

        warning_msgs.encode('utf-8', 'ignore')
        if warning_msgs:
            warning = {
                'title': _('Warning!'),
                'message': warning_msgs
            }
            res['warning'] = warning
            return res

    @api.onchange(
        'fal_real_amount', 'currency_id', 'quantity',
        'product_id', 'fal_real_currency')
    def _onchange_for_accepted_amount(self):
        if not self.product_id.fal_refund_cost_price:
            amount = self.fal_real_amount
            real_cur_id = self.fal_real_currency
            cur_id = self.currency_id
            if real_cur_id != cur_id:
                amount = real_cur_id.compute(
                    amount, cur_id, round=True)
            self.fal_accepted_amount = amount
        else:
            taxes = self.tax_ids.with_context(round=False).compute_all(
                self.unit_amount, self.currency_id,
                self.quantity, self.product_id)
            self.fal_accepted_amount = taxes['total_included']

    @api.onchange('tax_ids')
    def onchange_expense_tax_line(self):
        data = []
        for item in self:
            if item.tax_ids:
                taxes = item.tax_ids.with_context(round=False).compute_all(
                    item.unit_amount, item.fal_real_currency,
                    item.quantity, item.product_id)['taxes']
                for tax in taxes:
                    vals = {
                        'expense_id': self.id,
                        'name': tax['name'],
                        'tax_id': tax['id'],
                        'amount': tax['amount'],
                        'base': tax['base'],
                        'manual': False,
                        'sequence': tax['sequence'],
                        'account_id': (
                            tax['account_id'] or item.account_id.id
                        ) or (tax['refund_account_id'] or item.account_id.id),
                    }
                    data.append((0, 0, vals))
        item.fal_expense_tax_line_ids = data

    # Compute Taxes at creation
    @api.multi
    def compute_taxes(self):
        expense_tax_obj = self.env['account.expense.tax']
        for item in self:
            self._cr.execute(
                "DELETE FROM account_expense_tax WHERE expense_id=%s",
                (item.id,)
            )
            self.invalidate_cache()

            taxes = item.tax_ids.with_context(round=False).compute_all(
                item.unit_amount, item.fal_real_currency,
                item.quantity, item.product_id)['taxes']
            for tax in taxes:
                vals = {
                    'expense_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'base': tax['base'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_id': (
                        tax['account_id'] or item.account_id.id
                    ) or (tax['refund_account_id'] or item.account_id.id),
                }
                expense_tax_obj.create(vals)

    @api.model
    def create(self, vals):
        res = super(HrExpense, self).create(vals)
        res.compute_taxes()
        return res

    # ==== Button Action ====
    @api.multi
    def fal_no_proof(self):
        for item in self:
            _groups = self.env['res.users'].browse(self._uid).groups_id
            ModelDataObj = self.env['ir.model.data']
            if ModelDataObj.xmlid_to_object(
                'hr.group_hr_user') in _groups \
                and ModelDataObj.xmlid_to_object(
                'hr.group_hr_manager') not in _groups \
                    and item.employee_id.user_id.id != self._uid:
                raise UserError(_('HR Officer can not change \
                    other employee\'s expense state.'))
            self.write({'fal_is_no_proof': True})

    # Tree View action
    @api.multi
    def action_open_form_view(self):
        context = dict(self.env.context or {})
        self.ensure_one()
        return{
            'name': _('Expense'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.expense',
            'view_id': self.env.ref('hr_expense.hr_expense_view_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': context,
            'target': 'current'
        }

    @api.multi
    def action_copy_line(self):
        context = dict(self.env.context or {})
        self.ensure_one()
        data = self.copy_data()
        for x in data:
            for k, v in x.items():
                default = 'default_%s' % k
                context[default] = v
        return{
            'name': _('Expense Line'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.expense',
            'view_id': self.env.ref('hr_expense.hr_expense_view_form').id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'current',
        }


class AccountExpenseTax(models.Model):
    _name = "account.expense.tax"
    _description = "Expense Tax"
    _order = 'sequence'

    expense_id = fields.Many2one(
        'hr.expense',
        string='Expense',
        ondelete='cascade',
        index=True)
    name = fields.Char(string='Tax Description', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', ondelete='restrict')
    account_id = fields.Many2one(
        'account.account', string='Tax Account', required=True, domain=[
            ('deprecated', '=', False)])
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic account')
    amount = fields.Monetary("Amount", digits=dp.get_precision('Product Price'))
    manual = fields.Boolean(default=True)
    sequence = fields.Integer(
        help="Gives the sequence order when displaying a list of invoice tax.")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='account_id.company_id',
        store=True,
        readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        related='expense_id.currency_id',
        store=True,
        readonly=True)
    base = fields.Monetary(string='Base', digits=dp.get_precision('Product Price'))
