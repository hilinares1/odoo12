# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from odoo.tools import ustr, DEFAULT_SERVER_DATE_FORMAT
import odoo.addons.decimal_precision as dp

# ---------------------------------------------------------
# Utils
# ---------------------------------------------------------


def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))


def strToDatetime(strdate):
    return datetime.strptime(strdate, DEFAULT_SERVER_DATE_FORMAT)


class FalProjectBudgetTags(models.Model):
    _name = 'fal.project.budget.tags'
    _description = "Controlling Tags"
    _order = 'sequence'

    sequence = fields.Integer(default=10)
    name = fields.Char('Name', size=128, translate=1)
    parent_id = fields.Many2one('fal.project.budget.tags', 'Parent Control Tags')
    type = fields.Selection(
        [('regular', 'Regular'),
         ('view', 'View')],
        'Type', required=1, default='regular')
    child_ids = fields.One2many('fal.project.budget.tags', 'parent_id', 'Child Control Tags', copy=False)

    _constraints = [(models.BaseModel._check_recursion, 'Circular references are not permitted between parent and childs', ['parent_id'])]


class FalProjectBudget(models.Model):
    _name = 'fal.project.budget'
    _description = 'Controlling'
    _inherit = ['mail.thread']
    _order = 'id desc'

    # Compute Field
    @api.multi
    def _compute_child_complete_ids(self, name=None, arg=None):
        for project_budget in self:
            project_budget.child_complete_ids = [
                c.id for c in project_budget.child_ids]

    @api.multi
    @api.depends('fal_project_budget_line_ids', 'fal_project_budget_line_ids.planned_amount', 'child_ids', 'child_ids.total_budget')
    def _compute_total_budget(self):
        for project_budget in self:
            total_planned_amount = 0.00
            for line in project_budget.fal_project_budget_line_ids:
                total_planned_amount += line.planned_amount
            for sub_budget in project_budget.child_ids:
                total_planned_amount += sub_budget.total_budget
            project_budget.total_budget = total_planned_amount

    @api.multi
    def _compute_total_qty(self):
        for project_budget in self.filtered(lambda r: not r.is_template):
            total_qty = 0.00
            for line in project_budget.fal_project_budget_line_ids:
                total_qty += line.product_qty
            project_budget.total_qty = total_qty

    @api.multi
    @api.depends('name', 'version', 'is_t0', 'is_template')
    def name_get(self):
        res = []
        for budget in self:
            name = "%s_%s" % (budget.name, budget.version)
            if budget.is_template:
                name += _(" [Template]")
            res += [(budget.id, name)]
        return res

    @api.multi
    @api.depends('name', 'version', 'is_t0')
    def _compute_display_name(self):
        for project_budget in self:
            project_budget.display_name = project_budget.name
            project_budget.display_name += "_v"
            project_budget.display_name += str(project_budget.version) \
                or "0"
            if project_budget.is_template:
                project_budget.display_name += " [Template]"

    # Compute Budget Layout
    @api.multi
    def get_total_cost(self, tag):
        tag_ids = []
        if tag == 'budget':
            if self.id:
                budget = self.search([('id', 'child_of', self.id)]).ids
                budget_lines = self.env['fal.project.budget.line']
                tag_ids = budget_lines.search([('fal_project_budget_id', 'in', budget)])
        elif tag == 'sale':
            tag_ids = self.project_budget_sale_line_ids
        elif tag == 'purchase':
            tag_ids = self.project_budget_purchase_line_ids
        elif tag == 'mission':
            tag_ids = self.project_budget_mission_expense_line_ids
        elif tag == 'employee':
            tag_ids = self.project_budget_employee_timesheeet_line_ids
        elif tag == 'workcenter':
            tag_ids = self.project_budget_workcenter_timesheet_line_ids
        total_cost = 0.0
        for line in tag_ids:
            total_cost += line.practical_amount
        return total_cost

    @api.multi
    def get_target(self, tag):
        if tag == 'sale':
            x = self.total_sale_line
        elif tag == 'purchase':
            x = self.total_cost_price_purchase_line
        elif tag == 'mission':
            x = self.total_cost_price_mission_expense_line
        elif tag == 'employee':
            x = self.total_cost_price_employee_timesheet_line
        elif tag == 'workcenter':
            x = self.total_cost_price_workcenter_timesheet_line
        y = (1 - self.margin_percentage / 100)
        target = 0.0
        if y:
            target = x / y
        return target

    @api.multi
    def get_line_tag(self, tag):
        data_obj = self.env['ir.model.data']
        mdl = 'fal_project_budget'
        if tag == 'sale':
            oid = 'fal_project_budget_tags_sales'
            res_id = '.'.join([mdl, oid])
        if tag == 'purchase':
            oid = 'fal_project_budget_tags_purchases'
            res_id = '.'.join([mdl, oid])
        if tag == 'mission':
            oid = 'fal_project_budget_tags_mission_expenses'
            res_id = '.'.join([mdl, oid])
        if tag == 'employee':
            oid = 'fal_project_budget_tags_employee_timesheets'
            res_id = '.'.join([mdl, oid])
        if tag == 'workcenter':
            oid = 'fal_project_budget_tags_workcenter_timesheets'
            res_id = '.'.join([mdl, oid])
        tag_id = data_obj.xmlid_to_res_id(res_id)
        budget_lines = self.env['fal.project.budget.line']

        # Search all Control line and it's child budget line
        lines = []
        if self.id:
            budget = self.search([('id', 'child_of', self.id)]).ids
            line_ids = budget_lines.search([('fal_project_budget_id', 'in', budget)])
            budget_lines |= line_ids.filtered(
                lambda x: tag_id in x.fal_budget_tags_ids.ids)

            if budget_lines:
                lines = [(6, 0, budget_lines.ids)]
        return lines

    @api.multi
    def _compute_project_budget(self):
        for x in self:
            x.project_budget_sale_line_ids = x.get_line_tag('sale')
            x.project_budget_purchase_line_ids = x.get_line_tag('purchase')
            x.project_budget_mission_expense_line_ids = x.get_line_tag('mission')
            x.project_budget_employee_timesheeet_line_ids = x.get_line_tag('employee')
            x.project_budget_workcenter_timesheet_line_ids = x.get_line_tag('workcenter')

            x.total_cost_price = x.get_total_cost('budget')
            x.total_sale_line = x.get_total_cost('sale')
            x.total_cost_price_purchase_line = x.get_total_cost('purchase')
            x.total_cost_price_mission_expense_line = x.get_total_cost('mission')
            x.total_cost_price_employee_timesheet_line = x.get_total_cost('employee')
            x.total_cost_price_workcenter_timesheet_line = x.get_total_cost('workcenter')

            x.target_sale_price = x.get_target('sale')
            x.target_sale_price_purchase_line = x.get_target('purchase')
            x.target_sale_price_mission_expense_line = x.get_target('mission')
            x.target_sale_price_employee_timesheet_line = x.get_target('employee')
            x.target_sale_price_workcenter_timesheet_line = x.get_target('workcenter')

    # For XML / View compute
    @api.multi
    def get_project_tag(self, tag):
        data_obj = self.env['ir.model.data']
        mdl = 'fal_project_budget'
        if tag == 'sale':
            oid = 'fal_project_budget_tags_sales'
            res_id = '.'.join([mdl, oid])
        if tag == 'purchase':
            oid = 'fal_project_budget_tags_purchases'
            res_id = '.'.join([mdl, oid])
        if tag == 'mission':
            oid = 'fal_project_budget_tags_mission_expenses'
            res_id = '.'.join([mdl, oid])
        if tag == 'employee':
            oid = 'fal_project_budget_tags_employee_timesheets'
            res_id = '.'.join([mdl, oid])
        if tag == 'workcenter':
            oid = 'fal_project_budget_tags_workcenter_timesheets'
            res_id = '.'.join([mdl, oid])
        tag_id = data_obj.xmlid_to_res_id(res_id)
        for project_budget in self:
            if tag_id in project_budget.fal_budget_tags_ids.ids:
                return True
            else:
                return False

    @api.multi
    @api.depends('fal_budget_tags_ids')
    def _project_has_tag(self):
        for bgt in self:
            bgt.has_tag_sale = bgt.get_project_tag('sale')
            bgt.has_tag_purchase = bgt.get_project_tag('purchase')
            bgt.has_tag_mission = bgt.get_project_tag('mission')
            bgt.has_tag_employee = bgt.get_project_tag('employee')
            bgt.has_tag_workcenter = bgt.get_project_tag('workcenter')

    # General Information
    number = fields.Char('Number', size=64, default='New', copy=False)
    name = fields.Char('Control Name', required=True, states={'done': [('readonly', True)]}, translate=1, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility='onchange')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'Confirmed'),
         ('validate', 'Validated'),
         ('done', 'Done')],
        'Status', index=True, readonly=True, copy=False, track_visibility='always', default='draft')
    responsible_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, states={'done': [('readonly', True)]}, track_visibility='onchange')
    date_from = fields.Date('Start Date', states={'done': [('readonly', True)]}, track_visibility='onchange')
    date_to = fields.Date('End Date', states={'done': [('readonly', True)]}, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.user.company_id, states={'done': [('readonly', True)]}, track_visibility='onchange')

    # Template
    is_template = fields.Boolean("Template", default=False)
    fal_project_budget_template_id = fields.Many2one('fal.project.budget', 'Control Template', domain="[('is_template','=', True)]")

    # Project
    project_id = fields.Many2one('account.analytic.account', 'Project', states={'done': [('readonly', True)]}, track_visibility='onchange')
    project_partner_id = fields.Many2one('res.partner', 'Customer', related='project_id.partner_id', states={'done': [('readonly', True)]}, track_visibility='onchange')

    # Parent Child
    type = fields.Selection(
        [('root', 'Root'),
         ('view', 'View'),
         ('regular', 'Regular')],
        'Type', required=1, default='root', states={'done': [('readonly', True)]}, track_visibility='onchange')
    parent_id = fields.Many2one('fal.project.budget', 'Parent Control', states={'done': [('readonly', True)]}, track_visibility='onchange')
    child_ids = fields.One2many('fal.project.budget', 'parent_id', 'Child Control', copy=True, states={'done': [('readonly', True)]})
    child_complete_ids = fields.Many2many('fal.project.budget', compute='_compute_child_complete_ids', string="Control Hierarchy")

    # Tags
    fal_budget_tags_ids = fields.Many2many('fal.project.budget.tags', 'fal_project_budget_sheet_tags_rel', 'budget_id', 'tag_id', 'Control Tags', domain="[('type', '!=', 'view')]", states={'done': [('readonly', True)]}, track_visibility='onchange')

    # Budget
    fal_project_budget_line_ids = fields.One2many('fal.project.budget.line', 'fal_project_budget_id', 'Control Item(s)', states={'done': [('readonly', True)]}, copy=True)
    total_budget = fields.Monetary('Total Budget', compute='_compute_total_budget')
    t0_total_budget = fields.Float('Total T0 Budget', digits=0, states={'done': [('readonly', True)]})
    total_qty = fields.Monetary('Total Qty', compute='_compute_total_qty')
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Currency", readonly=True, required=True)

    # Versioning
    is_t0 = fields.Boolean('Is T0', default=False, copy=False, track_visibility='onchange', states={'done': [('readonly', True)]},)
    version = fields.Integer('Version', copy=False, track_visibility='onchange')
    project_budget_latest_id = fields.Many2one('fal.project.budget', 'Latest Control', states={'done': [('readonly', True)]},)
    project_budget_history_ids = fields.One2many('fal.project.budget', 'project_budget_latest_id', 'Control History', domain=[('active', '=', False)], readonly=True)

    # Project Layout
    project_budget_sale_line_ids = fields.Many2many(
        'fal.project.budget.line', 'Control Sales Line',
        compute='_compute_project_budget'
    )
    project_budget_purchase_line_ids = fields.Many2many(
        'fal.project.budget.line', 'Control Purchases Line',
        compute='_compute_project_budget'
    )
    project_budget_mission_expense_line_ids = fields.Many2many(
        'fal.project.budget.line', 'Control Mission Expenses Line',
        compute='_compute_project_budget'
    )
    project_budget_employee_timesheeet_line_ids = fields.Many2many(
        'fal.project.budget.line', 'Control Employee Timesheeet Line',
        compute='_compute_project_budget',
    )
    project_budget_workcenter_timesheet_line_ids = fields.Many2many(
        'fal.project.budget.line', 'Control Workcenter Timesheet Line',
        compute='_compute_project_budget',
    )
    total_cost_price = fields.Float(
        'Total Cost Price',
        compute='_compute_project_budget')
    total_sale_line = fields.Float(
        'Total Sale',
        compute='_compute_project_budget')
    total_cost_price_purchase_line = fields.Float(
        'Total Cost Price For Purchase',
        compute='_compute_project_budget')
    total_cost_price_mission_expense_line = fields.Float(
        'Total Cost Price for Mission Expense',
        compute='_compute_project_budget')
    total_cost_price_employee_timesheet_line = fields.Float(
        'Total Cost Price for Timesheet',
        compute='_compute_project_budget')
    total_cost_price_workcenter_timesheet_line = fields.Float(
        'Total Cost Price for Workcenter timesheet',
        compute='_compute_project_budget')
    target_sale_price_purchase_line = fields.Float(
        'Compute Target Sale Price for Purchase Line',
        compute='_compute_project_budget')
    target_sale_price_mission_expense_line = fields.Float(
        'Compute Target Sale Price for Mission Expense Line',
        compute='_compute_project_budget')
    target_sale_price_employee_timesheet_line = fields.Float(
        'Compute Target Sale Price for Employee Line',
        compute='_compute_project_budget')
    target_sale_price_workcenter_timesheet_line = fields.Float(
        'Compute Target Sale Price for Workcenter Timesheet Line',
        compute='_compute_project_budget')
    target_sale_price = fields.Float(
        'Compute Target Sale Price',
        compute='_compute_project_budget')
    product_id = fields.Many2one('product.product', 'Product')
    margin_percentage = fields.Float('Margin Percentage(%)')
    has_tag_sale = fields.Boolean(
        'Has Tag Sale', compute='_project_has_tag')
    has_tag_purchase = fields.Boolean(
        'Has Tag Purchase', compute='_project_has_tag')
    has_tag_mission = fields.Boolean(
        'Has Tag Mission', compute='_project_has_tag')
    has_tag_employee = fields.Boolean(
        'Has Tag Employee', compute='_project_has_tag')
    has_tag_workcenter = fields.Boolean(
        'Has Tag Workcenter', compute='_project_has_tag')
    get_default_account_type = fields.Char(compute='_get_default_account_type')

    # Group Currency
    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    @api.depends('currency_id', 'group_currency_id', 'total_budget', 't0_total_budget')
    def _ifrs_budget_currency(self):
        for order in self:
            group_curr = order.group_currency_id
            if order.currency_id != group_curr:
                order.total_budget_group_curr = order.currency_id._convert(order.total_budget, group_curr, order.company_id, fields.Date.today())
                order.t0_total_budget_group_curr = order.currency_id._convert(order.t0_total_budget, group_curr, order.company_id, fields.Date.today())
            else:
                order.total_budget_group_curr = order.total_budget
                order.t0_total_budget_group_curr = order.t0_total_budget

    @api.depends(
        'currency_id', 'group_currency_id', 'total_cost_price',
        'target_sale_price', 'total_sale_line',
        'total_cost_price_purchase_line',
        'target_sale_price_purchase_line',
        'total_cost_price_employee_timesheet_line',
        'target_sale_price_employee_timesheet_line',
        'total_cost_price_mission_expense_line',
        'target_sale_price_mission_expense_line',
        'total_cost_price_workcenter_timesheet_line',
        'target_sale_price_workcenter_timesheet_line')
    def _ifrs_total_cost_currency(self):
        for order in self:
            group_curr = order.group_currency_id
            if order.currency_id != group_curr:
                order.total_cost_price_group_curr = order.currency_id._convert(order.total_cost_price, group_curr, order.company_id, fields.Date.today())
                order.total_sale_line_group_curr = order.currency_id._convert(order.total_sale_line, group_curr, order.company_id, fields.Date.today())
                order.target_sale_price_group_curr = order.currency_id._convert(order.target_sale_price, group_curr, order.company_id, fields.Date.today())
                order.total_cost_price_purchase_group_curr = order.currency_id._convert(order.total_cost_price_purchase_line, group_curr, order.company_id, fields.Date.today())
                order.target_sale_price_purchase_group_curr = order.currency_id._convert(order.target_sale_price_purchase_line, group_curr, order.company_id, fields.Date.today())
                order.total_cost_price_timesheet_group_curr = order.currency_id._convert(order.total_cost_price_employee_timesheet_line, group_curr, order.company_id, fields.Date.today())
                order.target_sale_price_timesheet_group_curr = order.currency_id._convert(order.target_sale_price_employee_timesheet_line, group_curr, order.company_id, fields.Date.today())
                order.total_cost_price_expense_group_curr = order.currency_id._convert(order.total_cost_price_mission_expense_line, group_curr, order.company_id, fields.Date.today())
                order.target_sale_price_expense_group_curr = order.currency_id._convert(order.target_sale_price_mission_expense_line, group_curr, order.company_id, fields.Date.today())
                order.total_cost_price_workcenter_group_curr = order.currency_id._convert(order.total_cost_price_workcenter_timesheet_line, group_curr, order.company_id, fields.Date.today())
                order.target_sale_price_workcenter_group_curr = order.currency_id._convert(order.target_sale_price_workcenter_timesheet_line, group_curr, order.company_id, fields.Date.today())
            else:
                order.total_cost_price_group_curr = order.total_cost_price
                order.total_sale_line_group_curr = order.total_sale_line
                order.target_sale_price_group_curr = order.target_sale_price
                order.total_cost_price_purchase_group_curr = order.total_cost_price_purchase_line
                order.target_sale_price_purchase_group_curr = order.target_sale_price_purchase_line
                order.total_cost_price_timesheet_group_curr = order.total_cost_price_employee_timesheet_line
                order.target_sale_price_timesheet_group_curr = order.target_sale_price_employee_timesheet_line
                order.total_cost_price_expense_group_curr = order.total_cost_price_mission_expense_line
                order.target_sale_price_expense_group_curr = order.target_sale_price_mission_expense_line
                order.total_cost_price_workcenter_group_curr = order.total_cost_price_workcenter_timesheet_line
                order.target_sale_price_workcenter_group_curr = order.target_sale_price_workcenter_timesheet_line

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        compute='_get_group_currency',
    )

    total_budget_group_curr = fields.Monetary(
        compute='_ifrs_budget_currency',
        string='IFRS Total Budget',
        help="The Total Budget in IFRS Currencies.",
    )

    t0_total_budget_group_curr = fields.Monetary(
        compute='_ifrs_budget_currency',
        string='IFRS T0 Total Budget',
        help="The T0 Total Budget in IFRS Currencies.",
    )

    total_cost_price_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Cost Price',
        help="The Total Cost Price in IFRS Currencies.",
    )

    # sale IFRS
    total_sale_line_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Sale',
        help="The Total Sale in IFRS Currencies.",
    )
    target_sale_price_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Compute Target Sale Price',
        help="The Compute Target Sale Price in IFRS Currencies.",
    )

    # purchase IFRS
    total_cost_price_purchase_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Cost Price For Purchase',
        help="The Total Cost Price For Purchase in IFRS Currencies.",
    )
    target_sale_price_purchase_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Compute Target Sale Price for Purchase Line',
        help="The Compute Target Sale Price for Purchase Line in IFRS Currencies.",
    )

    # timesheet
    total_cost_price_timesheet_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Cost Price for Timesheet',
        help="The Total Cost Price for Timesheet in IFRS Currencies.",
    )
    target_sale_price_timesheet_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Compute Target Sale Price for Employee Line',
        help="The Compute Target Sale Price for Employee Line in IFRS Currencies.",
    )

    # expense
    total_cost_price_expense_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Cost Price for Mission Expense',
        help="The Total Cost Price for Mission Expense in IFRS Currencies.",
    )
    target_sale_price_expense_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Compute Target Sale Price for Mission Expense Line',
        help="The Compute Target Sale Price for Mission Expense Line in IFRS Currencies.",
    )

    # workcenter
    total_cost_price_workcenter_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Total Cost Price for Workcenter timesheet',
        help="The Total Cost Price for Mission Expense in IFRS Currencies.",
    )
    target_sale_price_workcenter_group_curr = fields.Monetary(
        compute='_ifrs_total_cost_currency',
        string='IFRS Compute Target Sale Price for Mission Expense Line',
        help="The Compute Target Sale Price for Workcenter Timesheet Line in IFRS Currencies.",
    )

    @api.depends('type')
    def _get_default_account_type(self):
        if self.type != 'regular':
            self.get_default_account_type = 'view'
        else:
            self.get_default_account_type = 'normal'

    # Constrains
    @api.multi
    @api.constrains('project_id')
    def _check_project_budget(self):
        for pb in self:
            project_budgets = self.env['fal.project.budget'].search(
                [
                    ('type', '=', 'root'),
                    ('project_id', '=', pb.project_id.id),
                    ('active', '=', True),
                    ('state', 'in', ['validate']),
                ])
            if len(project_budgets) not in [0, 1]:
                err_msg = 'You can\'t create two or more controls ' \
                          'with same project.'
                raise ValidationError(
                    _(err_msg))
            project_budgets = self.env['fal.project.budget'].search(
                [
                    ('type', '=', 'root'),
                    ('project_id', '=', pb.project_id.id),
                    ('state', 'in', ['done']),
                ])
            if len(project_budgets) not in [0, 1]:
                err_msg = 'You can\'t create two or more controls ' \
                          'with same project.'
                raise ValidationError(
                    _(err_msg))

    @api.multi
    @api.constrains('fal_budget_tags_ids')
    def _check_fal_budget_tags_ids(self):
        for project_budget in self:
            sale_tag_id = self.env.ref(
                "fal_project_budget.fal_project_budget_tags_sales").id
            purchase_tag_id = self.env.ref(
                "fal_project_budget.fal_project_budget_tags_purchases"
            ).id
            mission_xmlid = "fal_project_budget."
            mission_xmlid += "fal_project_budget_tags_mission_expenses"
            mission_tag_id = self.env.ref(mission_xmlid).id
            employee_xmlid = "fal_project_budget."
            employee_xmlid += "fal_project_budget_tags_employee_timesheets"
            employee_tag_id = self.env.ref(employee_xmlid).id
            workcenter_xmlid = "fal_project_budget."
            workcenter_xmlid += "fal_project_budget_tags_workcenter_timesheets"
            workcenter_tag_id = self.env.ref(workcenter_xmlid).id
            if (
                len(project_budget.project_budget_sale_line_ids) > 0 and
                sale_tag_id not in project_budget.fal_budget_tags_ids.ids
            ) or (
                len(project_budget.project_budget_purchase_line_ids) > 0 and
                purchase_tag_id not in project_budget.fal_budget_tags_ids.ids
            ) or (
                len(
                    project_budget.project_budget_mission_expense_line_ids
                ) > 0 and
                mission_tag_id not in project_budget.fal_budget_tags_ids.ids
            ) or (
                len(
                    project_budget.project_budget_employee_timesheeet_line_ids
                ) > 0 and
                employee_tag_id not in project_budget.fal_budget_tags_ids.ids
            ) or (
                len(
                    project_budget.project_budget_workcenter_timesheet_line_ids
                ) > 0 and
                workcenter_tag_id not in project_budget.fal_budget_tags_ids.ids
            ):
                raise UserError(_(
                    'Error!\n'
                    'Cannot delete a tag that \
                    have record on the corresponding line.'))
            for project_budget_line_id \
                    in project_budget.fal_project_budget_line_ids:
                if project_budget_line_id.fal_budget_tags_ids \
                        not in project_budget.fal_budget_tags_ids:
                    raise UserError(_(
                        'Error!\n'
                        'Cannot delete a tag that \
                        have record on the corresponding line.'))

    # Onchange
    @api.onchange('type')
    def _onchange_type(self):
        res = {'domain': {'project_id': []}}
        if self.type in ['root', 'view']:
            res['domain'] = {
                'project_id': [('account_type', '=', 'view')],
            }
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            prod_margin = self.product_id.categ_id.fal_margin_percentage
            self.margin_percentage = prod_margin

    @api.onchange('is_template')
    def _onchange_template(self):
        res = {'domain': {'parent_id': [('is_template', '=', self.is_template)]}}
        return res

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if not self.fal_budget_tags_ids:
            self.fal_budget_tags_ids = self.parent_id.fal_budget_tags_ids
        self.product_id = self.parent_id.product_id

    # Create & Write
    @api.model
    def create(self, vals):
        if vals.get('number', 'New') == 'New':
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'fal.project.budget') or 'New'
        return super(FalProjectBudget, self).create(vals)

    # State Button
    @api.multi
    def budget_confirm(self):
        self.write({
            'state': 'confirm'
        })
        for budget_child in self.child_ids:
            budget_child.budget_confirm()
        return True

    @api.multi
    def budget_draft(self):
        self.write({
            'state': 'draft'
        })
        for budget_child in self.child_ids:
            budget_child.budget_draft()
        return True

    @api.multi
    def budget_validate(self):
        self.write({
            'state': 'validate',
        })
        for budget_child in self.child_ids:
            budget_child.budget_validate()
        return True

    @api.multi
    def budget_cancel(self):
        self.write({
            'state': 'cancel'
        })
        for budget_child in self.child_ids:
            budget_child.budget_cancel()
        return True

    @api.multi
    def budget_done(self):
        self.write({
            'state': 'done'
        })
        for budget_child in self.child_ids:
            budget_child.budget_done()
        return True

    # Function Button
    @api.multi
    def budget_revision(self):
        self.ensure_one()

        # Copy the Budget
        cp_budget = self.copy(default={'child_ids': False})

        versi = self.version + 1
        cp_budget.write({
            'version': versi,
            'project_budget_history_ids': [(6, 0, [self.id] + self.project_budget_history_ids.ids)],
        })

        for child in self.child_ids:
            new_child = child.budget_revision()
            new_child.parent_id = cp_budget.id

        # Make old budget inactive
        self.write({
            'active': False,
        })
        return cp_budget

    @api.multi
    def generate_budget_based_on_template(self):
        self.ensure_one()
        new_control = self.copy(dict(is_template=0, active=1))
        for control_child in self.search([('id', 'child_of', new_control.id)]):
            control_child.write({'is_template': False, 'active': True, 'fal_project_budget_template_id': self.id})

        wizard_id = self.env['fal.template.budget.fill.data.wizard'].create({
            'fal_project_budget_id': new_control.id,
            'fal_project_budget_ids': [(6, 0, self.search([('id', 'child_of', [new_control.id])]).ids)]
        })

        ref_id = 'fal_project_budget.fal_template_budget_fill_data_wizard_form'
        view_id = self.env.ref(ref_id).id
        return {
            'name': _('Control Fill'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.template.budget.fill.data.wizard',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': wizard_id.id,
            'context': self.env.context,
            'target': 'new'
        }

    @api.multi
    def create_budget_line(self):
        self.ensure_one()
        context = dict(self._context or {})
        # Set up default field
        if context['default_fal_budget_tags_ids']:
            context['default_fal_budget_tags_ids'] = [(6, 0, [self.env.ref(context['default_fal_budget_tags_ids']).id])]
        context['fill_control'] = True

        ref_id = 'fal_project_budget.view_fal_project_budget_line_form'
        view_id = self.env.ref(ref_id).id
        return {
            'name': _('Control Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.project.budget.line',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def edit_budget(self):
        self.ensure_one()
        context = dict(self._context or {})

        ref_id = 'fal_project_budget.fal_project_budget_view_form'
        view_id = self.env.ref(ref_id).id
        return {
            'name': _('Control'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.project.budget',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': context,
            'res_id': self.id,
            'target': 'new'
        }


class FalProjectBudgetLine(models.Model):
    _name = 'fal.project.budget.line'
    _description = "Control Line"

    @api.multi
    @api.depends('name', 'parent_template', 'fal_project_budget_id')
    def name_get(self):
        res = []
        for budget_line in self:
            name = "[%s] %s" % (budget_line.fal_project_budget_id.display_name, budget_line.name)
            if budget_line.parent_template:
                name += _(" [Template]")
            res += [(budget_line.id, name)]
        return res

    # Compute Field
    def _compute_theoritical_amount(self):
        for line in self.filtered(lambda r: not r.parent_template and r.date_to and r.date_from):
            today = datetime.now()
            wizard_date_from = self.env.context.get('wizard_date_from')
            wizard_date_to = self.env.context.get('wizard_date_to')
            # Used for the report
            if wizard_date_from and wizard_date_to:
                date_from = wizard_date_from
                date_to = wizard_date_to
                if date_from < line.date_from:
                    date_from = line.date_from
                elif date_from > line.date_to:
                    date_from = False

                if date_to > line.date_to:
                    date_to = line.date_to
                elif date_to < line.date_from:
                    date_to = False

                theo_amt = 0.00
                if date_from and date_to:
                    dt = line.date_to
                    df = line.date_from
                    ltd = dt - df
                    etd = date_to - date_from
                    if etd.days > 0:
                        epl = (etd.total_seconds() / ltd.total_seconds())
                        theo_amt = epl * line.planned_amount
            else:
                if line.paid_date:
                    if strToDate(line.date_to) <= strToDate(line.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    dt = line.date_to
                    df = line.date_from
                    ltd = dt - df
                    etd = today - strToDatetime(str(line.date_from))

                    if etd.days < 0:
                        # If the budget line has not started yet,
                        # theoretical amount should be zero
                        theo_amt = 0.00
                    elif ltd.days > 0 and today < strToDatetime(str(line.date_to)):
                        # If today is between the budget line date_from
                        # and date_to
                        # from pudb import set_trace; set_trace()
                        epl = (etd.total_seconds() / ltd.total_seconds())
                        theo_amt = epl * line.planned_amount
                    else:
                        theo_amt = line.planned_amount
            line.theoritical_amount = theo_amt

    @api.multi
    def _compute_practical_amount_currency(self):
        for line in self.filtered(lambda r: not r.parent_template and r.date_to and r.date_from):
            acc_ids = [x.id for x in line.general_budget_id.account_ids]
            if line.account_id:
                acc_ids = [line.account_id.id]
            if not acc_ids:
                raise UserError((
                    "The Budget has no accounts!"))
            practical_amount = 0
            fal_practical_amount_currency = 0
            for acc_id in acc_ids:
                date_to = self.env.context.get('wizard_date_to') or line.date_to
                date_from = self.env.context.get('wizard_date_from') or line.date_from

                query_select = """
                    SELECT SUM(credit), sum(debit), sum(amount_currency)
                    FROM account_move_line AS line
                    LEFT OUTER JOIN product_product pp ON
                    line.product_id = pp.id
                    LEFT OUTER JOIN product_template pt ON
                    pp.product_tmpl_id = pt.id
                """
                query_where = """
                    WHERE account_id=ANY(%s) AND
                    (date between to_date(%s,'yyyy-mm-dd') AND
                    to_date(%s,'yyyy-mm-dd'))
                """
                tuple_list = ([acc_id], str(date_from), str(date_to))

                if line.project_id.id:
                    query_where += "AND analytic_account_id = %s "
                    tuple_list += (line.project_id.id,)
                if line.partner_ids.ids:
                    query_where += "AND partner_id in %s "
                    tuple_list += (tuple(line.partner_ids.ids),)
                if line.product_ids.ids:
                    query_where += "AND product_id in %s "
                    tuple_list += (tuple(line.product_ids.ids),)
                if line.product_category_ids.ids:
                    query_where += "AND pt.categ_id in %s "
                    tuple_list += (tuple(self.env['product.category'].search([('id', 'child_of', line.product_category_ids.ids)]).ids),)

                self.env.cr.execute(query_select + query_where, tuple_list)
                res = self.env.cr.fetchone()

                # no need to split credit debit account.

                # acc = self.env['account.account'].browse(acc_id)
                # if acc.user_type_id in [
                #     self.env.ref('account.data_account_type_receivable'),
                #     self.env.ref('account.data_account_type_payable'),
                #     self.env.ref('account.data_account_type_liquidity'),
                #     self.env.ref('account.data_account_type_credit_card'),
                #     self.env.ref('account.data_account_type_current_assets'),
                #     self.env.ref('account.data_account_type_non_current_assets'),
                #     self.env.ref('account.data_account_type_prepayments'),
                #     self.env.ref('account.data_account_type_fixed_assets'),
                #     self.env.ref('account.data_account_type_depreciation'),
                #     self.env.ref('account.data_account_type_expenses'),
                #     self.env.ref('account.data_account_type_direct_costs'),
                # ]:
                #     practical_amount += (res[1] or 0.0) - (res[0] or 0.0)
                #     fal_practical_amount_currency += res[2] or 0.0
                # else:
                practical_amount += (res[0] or 0.0) - (res[1] or 0.0)
                fal_practical_amount_currency += res[2] or 0.0
            line.practical_amount = practical_amount
            line.fal_practical_amount_currency = fal_practical_amount_currency

    @api.multi
    def _compute_percentage(self):
        for line in self.filtered(lambda r: not r.parent_template and r.date_to and r.date_from):
            if line.theoritical_amount != 0.00:
                percentage = float(
                    (line.practical_amount or 0.0) / line.theoritical_amount)
                line.percentage = percentage * 100
            else:
                line.percentage = 0

    # Default Value
    @api.model
    def _default_fal_budget_tags_ids(self):
        return self.env.context.get('budget_tags', [])

    # General Info
    name = fields.Char('Name', size=128, translate=1, help="""Budget Line Name.""", required=True, states={'done': [('readonly', True)]})
    reference = fields.Char('Reference', size=128, states={'done': [('readonly', True)]})
    number = fields.Char('Number', size=128, states={'done': [('readonly', True)]})

    fal_project_budget_id = fields.Many2one('fal.project.budget', 'Control')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=False, states={'done': [('readonly', True)]})
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)], required=True)
    date_from = fields.Date('Start Date', states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', states={'done': [('readonly', True)]})
    paid_date = fields.Date('Paid Date', states={'done': [('readonly', True)]})
    company_id = fields.Many2one('res.company', related='fal_project_budget_id.company_id', string='Company', store=True, readonly=True, states={'done': [('readonly', True)]})

    # Parent Info
    parent_active = fields.Boolean('Active', related="fal_project_budget_id.active")
    parent_template = fields.Boolean("Template", related="fal_project_budget_id.is_template")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('cancel', 'Cancelled'),
         ('confirm', 'Confirmed'),
         ('validate', 'Validated'),
         ('done', 'Done')],
        'Status', related="fal_project_budget_id.state")
    project_id = fields.Many2one('account.analytic.account', related="fal_project_budget_id.project_id", string="Project", store=True, readonly=True)

    # Amount
    planned_amount = fields.Float('Planned Amount', required=True, digits=0, states={'done': [('readonly', True)]})
    t0_planned_amount = fields.Float('T0 Planned Amount', digits=0, states={'done': [('readonly', True)]})
    practical_amount = fields.Float(compute='_compute_practical_amount_currency', string='Realized Amount', type='float', digits=0)
    theoritical_amount = fields.Float(compute='_compute_theoritical_amount', string='Theoretical Amount', type='float', digits=0)
    percentage = fields.Float(compute='_compute_percentage', string='Achievement', type='float')
    fal_practical_amount_currency = fields.Monetary(compute='_compute_practical_amount_currency', string='Realized Amount Currency', digits=0)

    # Tags
    fal_budget_tags_ids = fields.Many2many('fal.project.budget.tags', 'fal_project_budget_tags_rel', 'budget_id', 'tag_id', 'Control Tags', domain="[('type', '!=', 'view')]", states={'done': [('readonly', True)]})

    # Budget Limitation
    partner_ids = fields.Many2many('res.partner', 'fal_project_budget_line_partner_rel', 'project_budget_line_id', 'partner_id', string='Partner(s)', states={'done': [('readonly', True)]})
    product_ids = fields.Many2many('product.product', 'fal_project_budget_line_product_rel', 'project_budget_line_id', 'product_id', string='Product(s)', states={'done': [('readonly', True)]})
    product_category_ids = fields.Many2many('product.category', 'fal_project_budget_line_product_category_rel', 'project_budget_line_id', 'product_category_id', string='Product Category(es)', states={'done': [('readonly', True)]})
    product_qty = fields.Float('Quantity', default=1, states={'done': [('readonly', True)]})
    product_unit_price = fields.Monetary('Unit Price', digits=dp.get_precision('Account'), states={'done': [('readonly', True)]})
    employee_id = fields.Many2one('hr.employee', 'Employee', states={'done': [('readonly', True)]})
    currency_id = fields.Many2one("res.currency", related='company_id.currency_id', string="Currency", readonly=True, required=True)

    # Onchange
    @api.onchange('fal_project_budget_id')
    def onchange_fal_project_budget_id(self):
        ids = []
        if self.fal_project_budget_id.fal_budget_tags_ids:
            ids = self.fal_project_budget_id.fal_budget_tags_ids.ids
        if self.fal_project_budget_id.date_from:
            self.date_from = self.fal_project_budget_id.date_from
        if self.fal_project_budget_id.date_to:
            self.date_to = self.fal_project_budget_id.date_to
        return {'domain': {'fal_budget_tags_ids': [('id', 'in', ids)]}}

    @api.onchange('product_qty', 'product_unit_price')
    def _onchange_product_qty_unit_price(self):
        self.planned_amount = self.product_qty * self.product_unit_price

    # Create & Write
    @api.model
    def create(self, vals):
        if vals.get('number', 'New') == 'New':
            vals['number'] = self.env['ir.sequence'].next_by_code(
                'fal.project.budget.line') or 'New'
        return super(FalProjectBudgetLine, self).create(vals)

    @api.multi
    def edit_budget_line(self):
        self.ensure_one()
        context = dict(self._context or {})

        ref_id = 'fal_project_budget.view_fal_project_budget_line_form'
        view_id = self.env.ref(ref_id).id
        return {
            'name': _('Control Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.project.budget.line',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': context,
            'res_id': self.id,
            'target': 'new'
        }

# end of FalProjectBudgetLine()
