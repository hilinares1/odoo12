# -*- encoding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero
from odoo.tools.safe_eval import safe_eval


class account_aspone(models.Model):
    _name = 'account.aspone'

    name = fields.Char('Name')
    date_start = fields.Date("Start", required=True)
    date_end = fields.Date("End", required=True)
    aspone_line_ids = fields.One2many('account.aspone.line', 'aspone_line_id', string='Lines')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id)

    def compute(self):
        for lines in self.aspone_line_ids:
            parameters = {}
            for formula in lines.formula_parameter_ids:
                tax_base_amount_total = 0
                if formula.tax_id.tax_exigibility == 'on_payment':
                    tax_base_amount_total = sum(aml.tax_base_amount for aml in self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('tax_exigible', '=', True), ('company_id', '=', self.env.user.company_id.id), ('date', '>=', self.date_start), ('date', '<=', self.date_end), '|', ('tax_ids', 'in', formula.tax_id.ids), ('tax_line_id', '=', formula.tax_id.id)]))
                else:
                    tax_base_amount_total = sum(aml.tax_base_amount for aml in self.env['account.move.line'].search([('move_id.state', '=', 'posted'), ('company_id', '=', self.env.user.company_id.id), ('date', '>=', self.date_start), ('date', '<=', self.date_end), '|', ('tax_ids', 'in', formula.tax_id.ids), ('tax_line_id', '=', formula.tax_id.id)]))
                parameters[formula.code] = tax_base_amount_total
            lines.result = safe_eval(lines.formula, parameters)


class account_aspone_line(models.Model):
    _name = 'account.aspone.line'

    aspone_line_id = fields.Many2one('account.aspone', string='ASPONE report')
    xml_name = fields.Char('XML Name', required=True)
    report_table = fields.Char("Table")
    report_row = fields.Char("Row")
    formula = fields.Text(string='Python Code', required=True)
    formula_parameter_ids = fields.One2many('account.aspone.parameter', 'aspone_line_id')
    result = fields.Monetary(default=0.0, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', related='aspone_line_id.currency_id', store=True)


class account_aspone_parameter(models.Model):
    _name = 'account.aspone.parameter'

    aspone_line_id = fields.Many2one('account.aspone.line', 'Line')
    code = fields.Char("Code", required=True)
    tax_id = fields.Many2one('account.tax', string="Tax", required=True)


# end of account_asset_category()
