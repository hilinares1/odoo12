# -*- encoding: utf-8 -*-

import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import float_compare, float_is_zero


class account_asset_category(models.Model):
    _inherit = 'account.asset.category'

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if any(not asset_category._check_recursion() for asset_category in self):
            raise ValidationError(_("Error! You can't create recursive hierarchy of Activity."))

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        # Copy all parent info
        if self.parent_id:
            self.journal_id = self.parent_id.journal_id
            self.account_asset_id = self.parent_id.account_asset_id
            self.account_depreciation_id = self.parent_id.account_depreciation_id
            self.account_depreciation_expense_id = self.parent_id.account_depreciation_expense_id
            self.method_time = self.parent_id.method_time
            self.method_number = self.parent_id.method_number
            self.method_period = self.parent_id.method_period
            self.method_end = self.parent_id.method_end
            self.method = self.parent_id.method
            self.method_progress_factor = self.parent_id.method_progress_factor
            self.open_asset = self.parent_id.open_asset
            self.group_entries = self.parent_id.group_entries
            self.date_first_depreciation = self.parent_id.date_first_depreciation

    fal_type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal')
    ], 'Type', required=True, default='normal')
    parent_id = fields.Many2one(
        'account.asset.category', 'Parent Category',
        domain="[('fal_type', '=', 'view')]")
    child_ids = fields.One2many(
        'account.asset.category', 'parent_id',
        'Children(s)', copy=False)

# end of account_asset_category()


class account_asset_asset(models.Model):
    _inherit = 'account.asset.asset'

    @api.multi
    @api.depends('depreciation_line_ids')
    def _fal_closing_date(self):
        for record in self:
            temp_last_date = False
            for line in record.depreciation_line_ids:
                if temp_last_date:
                    if temp_last_date < line.depreciation_date:
                        temp_last_date = line.depreciation_date
                else:
                    temp_last_date = line.depreciation_date
            record.fal_closing_date = temp_last_date

    fal_closing_date = fields.Date(
        string='Closing Date',
        help="The Closing Date",
        compute='_fal_closing_date',
        store=True
    )
    fal_purchase_date = fields.Date(
        'Purchase Date', readonly=True,
        states={'draft': [('readonly', False)]})
    fal_original_purchase_value = fields.Float(
        'Purchase Value', readonly=True,
        digits=0, states={'draft': [('readonly', False)]})
    fal_use_purchase_value = fields.Boolean("Use Purchase Value", help="Use Purchase Value instead of Gross Value")
    fal_second_depreciation_date = fields.Date(
        'Second Depreciation Date', readonly=True,
        states={'draft': [('readonly', False)]})
    fal_asset_number = fields.Char('Asset Number', size=64)
    date_first_depreciation = fields.Selection(selection_add=[('end_of_last_moth', 'Last Day of Month')])

    @api.one
    @api.depends('value', 'salvage_value', 'depreciation_line_ids.move_check', 'depreciation_line_ids.amount', 'fal_use_purchase_value', 'fal_original_purchase_value')
    def _amount_residual(self):
        total_amount = 0.0
        for line in self.depreciation_line_ids:
            if line.move_check:
                total_amount += line.amount
        # Change Start Here
        # Use Purchase Value instead
        if self.fal_use_purchase_value:
            self.value_residual = self.fal_original_purchase_value - total_amount - self.salvage_value
        # Change End Here
        else:
            self.value_residual = self.value - total_amount - self.salvage_value

    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()

        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual

            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
            else:
                # depreciation_date computed from the purchase date
                depreciation_date = self.date
                if self.date_first_depreciation == 'last_day_period':
                    # depreciation_date = the last day of the month
                    depreciation_date = depreciation_date + relativedelta(day=31)
                    # ... or fiscalyear depending the number of period
                    if self.method_period == 12:
                        depreciation_date = depreciation_date + relativedelta(month=self.company_id.fiscalyear_last_month)
                        depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
                        if depreciation_date < self.date:
                            depreciation_date = depreciation_date + relativedelta(years=1)
                elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
                    # depreciation_date set manually from the 'first_depreciation_manual_date' field
                    depreciation_date = self.first_depreciation_manual_date
                # Change Start Here
                # Handle the option to depreciate always at the end of month
                elif self.date_first_depreciation == 'end_of_last_moth':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)
                # Change End Here

            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date,
                }
                commands.append((0, False, vals))

                # Change Start Here
                # Handle the change of 2nd depreciation date
                if len(posted_depreciation_line_ids) == 0 and self.date_first_depreciation == 'manual' and self.fal_second_depreciation_date and sequence == 1:
                    depreciation_date = self.fal_second_depreciation_date
                    month_day = self.fal_second_depreciation_date.day
                else:
                    depreciation_date = depreciation_date + relativedelta(months=+self.method_period)
                # Change End Here

                if month_day > 28 and self.date_first_depreciation == 'manual':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))
                # Change Start Here
                # Handle the option to depreciate always at the end of month
                elif self.date_first_depreciation == 'end_of_last_moth':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)
                # Change End Here

                # datetime doesn't take into account that the number of days is not the same for each month
                if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)

        self.write({'depreciation_line_ids': commands})

        return True

    @api.model
    def create(self, vals):
        vals['fal_asset_number'] = self.env['ir.sequence'].\
            next_by_code('fal.account.asset.asset') or 'New'
        return super(account_asset_asset, self).create(vals)
