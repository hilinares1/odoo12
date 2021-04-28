# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class fal_account_periods_lock(models.Model):
    _inherit = "fal.account.periods.lock"

    lock_gap_days_employee = fields.Integer(
        'Lock Gap Days Employee', default=2)
    lock_gap_days_manager = fields.Integer('Lock Gap Days Manager', default=5)

    def prepare_account_period_lock_line_vals(self, interval, fy, ds):
        res = super(
            fal_account_periods_lock, self
        ).prepare_account_period_lock_line_vals(interval, fy, ds)

        de = ds + relativedelta(months=interval, days=-1)
        employee_lock_de = de + relativedelta(days=fy.lock_gap_days_employee)
        manager_lock_de = de + relativedelta(days=fy.lock_gap_days_manager)

        res['employee_locking_date'] = employee_lock_de.strftime('%Y-%m-%d')
        res['manager_locking_date'] = manager_lock_de.strftime('%Y-%m-%d')
        return res

    # run on demo data
    @api.multi
    def remove_line(self):
        periods = self.search(([]))
        for period in periods:
            period.period_ids.unlink()
            period.create_period1()

# end of fal_account_periods_lock()


class fal_account_periods_lock_line(models.Model):
    _inherit = "fal.account.periods.lock.line"

    # add default data to fix error on odoo.sh, remove this if no needed
    def _default_employee_manager_locking(self):
        date = fields.Date.today() + relativedelta(months=1, days=-1)
        return date

    employee_locking_date = fields.Date(
        'Employee locking Date', required=True,
        default=_default_employee_manager_locking)
    manager_locking_date = fields.Date(
        'Manager locking Date', required=True,
        default=_default_employee_manager_locking)

    @api.model
    def _check_lock_date_hr(self, dt=None, company_id=None):
        if company_id:
            period_ids = self.with_context(company_id=company_id).find(dt)
        else:
            period_ids = self.find(dt)
        if period_ids:
            lock_date = period_ids[0].employee_locking_date
            if self._context.get('get_active_model') == "hr.expense":
                if self.user_has_groups('hr_expense.group_hr_expense_manager'):
                    lock_date = period_ids[0].manager_locking_date
            elif self._context.get('get_active_model') == "account.analytic.line":
                if self.user_has_groups('hr_timesheet.group_timesheet_manager'):
                    lock_date = period_ids[0].manager_locking_date
            if fields.date.today() >= lock_date:
                raise UserError(_(
                    "You cannot add/modify entries prior to and inclusive of the lock \
                    date %s. Check the company settings or ask someone \
                    with the 'Adviser' role") % (lock_date))

# end of fal_account_periods_lock_line


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def create(self, vals):
        if not vals.get('message_follower_ids', False):
            odoobot = self.env.ref("base.partner_root")
            if self.env.user.partner_id != odoobot:
                period_line_obj = self.env['fal.account.periods.lock.line']
                if vals.get('date', False):
                    if vals.get('company_id', False):
                        period_line_obj.with_context(get_active_model='hr.expense')._check_lock_date_hr(vals['date'], vals['company_id'])
                    else:
                        period_line_obj.with_context(get_active_model='hr.expense')._check_lock_date_hr(vals['date'], self.env.user.company_id.id)
        return super(HrExpense, self).create(vals)

    @api.multi
    def write(self, vals):
        if not vals.get('message_follower_ids', False):
            odoobot = self.env.ref("base.partner_root")
            period_line_obj = self.env['fal.account.periods.lock.line']
            for expense in self:
                if self.env.user.partner_id != odoobot:
                    period_line_obj.with_context(get_active_model='hr.expense')._check_lock_date_hr(dt=expense.date, company_id=expense.company_id.id)
        return super(HrExpense, self).write(vals)

# end of HrExpense()


class account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def create(self, vals):
        period_line_obj = self.env['fal.account.periods.lock.line']
        odoobot = self.env.ref("base.partner_root")
        if self.env.user.partner_id != odoobot:
            if vals.get('date', False):
                # It's not clean at all to use self.env.user
                # Find another solution later
                # only check analytic line with project
                if vals.get('project_id', False):
                    period_line_obj.with_context(get_active_model='account.analytic.line')._check_lock_date_hr(vals['date'], self.env.user.company_id.id)
        return super(account_analytic_line, self).create(vals)

    @api.multi
    def write(self, vals):
        period_line_obj = self.env['fal.account.periods.lock.line']
        odoobot = self.env.ref("base.partner_root")
        for analytic_line in self:
            if self.env.user.partner_id != odoobot:
                # It's not clean at all to use self.env.user
                # Find another solution later
                # only check analytic line with project
                if analytic_line.project_id:
                    period_line_obj.with_context(get_active_model='account.analytic.line')._check_lock_date_hr(dt=analytic_line.date, company_id=self.env.user.company_id.id)
        return super(account_analytic_line, self).write(vals)

# end of account_analytic_line()
