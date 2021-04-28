# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
import time
import calendar
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

class AccountAccount(models.Model):
    _inherit = "account.account"
    _description = "Account"

    tag_ids = fields.Many2many('account.account.tag',
                               'account_account_account_tag', string='Tags',
                               help="Optional tags you may want to assign for custom reporting")

    def get_date_from_filter(self, cr, uid, filter, context=None):
        '''
        Función para obtener la fecha de los filtros de fecha.
        :param filter: dictionary
                {u'disabled': False, u'text': u'This month', u'locked': False, u'id': u'this_month', u'element': [{}]}
        :return: date_from and date_to
        '''
        if filter.get('id'):
            date = datetime.today()
            if filter['id'] == 'today':
                date_from = date.strftime("%Y-%m-%d")
                date_to = date.strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_week':
                day_today = date - timedelta(days=date.weekday())
                date_from = (day_today - timedelta(
                    days=date.weekday())).strftime("%Y-%m-%d")
                date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_month':
                date_from = datetime(date.year, date.month, 1).strftime(
                    "%Y-%m-%d")
                date_to = datetime(date.year, date.month,
                                   calendar.mdays[date.month]).strftime(
                    "%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 3,
                                       calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # First quarter
                    date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 6,
                                       calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # First quarter
                    date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 9,
                                       calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # First quarter
                    date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 12,
                                       calendar.mdays[12]).strftime("%Y-%m-%d")
                return date_from, date_to
            if filter['id'] == 'this_financial_year':
                date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(day=1))
            if filter['id'] == 'yesterday':
                date_from = date.strftime("%Y-%m-%d")
                date_to = date.strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(day=7))
            if filter['id'] == 'last_week':
                day_today = date - timedelta(days=date.weekday())
                date_from = (day_today - timedelta(
                    days=date.weekday())).strftime("%Y-%m-%d")
                date_to = (day_today + timedelta(days=6)).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(months=1))
            if filter['id'] == 'last_month':
                date_from = datetime(date.year, date.month, 1).strftime(
                    "%Y-%m-%d")
                date_to = datetime(date.year, date.month,
                                   calendar.mdays[date.month]).strftime(
                    "%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(months=3))
            if filter['id'] == 'last_quarter':
                if int((date.month - 1) / 3) == 0:  # First quarter
                    date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 3,
                                       calendar.mdays[3]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 1:  # Second quarter
                    date_from = datetime(date.year, 4, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 6,
                                       calendar.mdays[6]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 2:  # Third quarter
                    date_from = datetime(date.year, 7, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 9,
                                       calendar.mdays[9]).strftime("%Y-%m-%d")
                if int((date.month - 1) / 3) == 3:  # Fourth quarter
                    date_from = datetime(date.year, 10, 1).strftime("%Y-%m-%d")
                    date_to = datetime(date.year, 12,
                                       calendar.mdays[12]).strftime("%Y-%m-%d")
                return date_from, date_to
            date = (datetime.now() - relativedelta(years=1))
            if filter['id'] == 'last_financial_year':
                date_from = datetime(date.year, 1, 1).strftime("%Y-%m-%d")
                date_to = datetime(date.year, 12, 31).strftime("%Y-%m-%d")
                return date_from, date_to

    def _get_fiscalyear(self, cr, uid, context=None):
        """
        Función para obtener el año fiscal.
        :param cr:
        :param uid:
        :param context:
        :return:fiscalyears
        """
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<=', now), ('date_stop', '>=', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    def create_wizard(self, cr, uid, filters, context=None):
        """
        Función para crear el wizard que genera el reporte xls.
        :param cr:
        :param uid:
        :param filters:
        :param context:
        :return: wizard
        """
        ctx = {}
        ctx.update({'active_model': 'general.ledger.webkit',
                    'xls_export': 1})
        target_move = 'all'
        if filters.get('all_posted', False):
            target_move = 'posted'

        display_account = 'bal_all'
        if filters.get('all_balance_not_zero', False):
            display_account = 'bal_mix'

        partner_ids = filters.get('partner_ids', False)
        partner_list = []
        for partner in partner_ids:
            partner_list.append((4, partner))

        unit_ids = filters.get('unit_ids', [])
        unit_list = []
        for unit in unit_ids:
            unit_list.append((4, unit))

        if filters.get('date_filter', False):
            date_from, date_to = self.get_date_from_filter(cr, uid,
                                           filters.get('date_filter')[0], context)
        else:
            date_from = filters.get('date_from', False)
            date_to = filters.get('date_to', False)

        # Si se marca mostrar el saldo inicial, se debe pasar el año fiscal para que se muestre el saldo en el xlsx
        domain = [('date_start', '<=', date_from), ('date_stop', '>=', date_to)]
        if self.pool.get('res.users').browse(cr, uid, uid).company_id:
            domain.append(('company_id', '=', self.pool.get('res.users').browse(cr, uid, uid).company_id.id))
        fiscal_year_id = self.pool['account.fiscalyear'].search(cr, uid, domain, limit=1)

        if filters.get('show_currency', False):
            display_curr_columns = True
            curr_rate_date = False
            curr_rate_option = 'trans_date'
            curr_rate = 0.0
            if filters.get('set_date', False):
                curr_rate_date = filters.get('curr_rate_date', False)
                curr_rate_option = 'set_date'
            elif filters.get('set_curr_date', False):
                curr_rate = float(filters.get('curr_rate')) if \
                    filters.get('curr_rate', False) else False
                curr_rate_option = 'set_curr_rate'
        else:
            display_curr_columns = False
            curr_rate_date = False
            curr_rate_option = ''
            curr_rate = False

        values = {
             'account_ids': [(6, 0, filters.get('account_ids', []))],
             'centralize': False,
             'chart_account_id': 1,
             'periods': [],
             'period_to': False,
             'period_from': False,
             'journal_ids': [(6, 0, filters.get('journal_ids', []))],
             'filter_operating_unit_ids': unit_list,
             'filter_partner_ids': partner_list,
             'fiscalyear_id': (filters.get('initial_balance') and fiscal_year_id) and fiscal_year_id[0] or False,

             'date_to': date_to,
             'date_from': date_from,
             'curr_rate_option': curr_rate_option,
             'display_curr_columns': display_curr_columns,
             'curr_rate_date': curr_rate_date,
             'curr_rate': curr_rate,
             'filter': 'filter_date',

             'amount_currency': False,
             'display_account': display_account,
             'target_move': target_move,
        }
        wizard = self.pool.get('general.ledger.webkit').create(cr, uid, values,
                                                               ctx)
        return wizard

class AccountAccountTag(models.Model):
    _name = 'account.account.tag'
    _description = 'Account Tag'

    name = fields.Char(required=True)
    applicability = fields.Selection([('accounts', 'Accounts'), ('taxes', 'Taxes')], required=True, default='accounts')
    color = fields.Integer('Color Index', default=10)
    active = fields.Boolean(default=True, help="Set active to false to hide the Account Tag without removing it.")