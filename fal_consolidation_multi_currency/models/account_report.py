# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_ifrs = None

    def _set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('ifrs'):
            ctx['ifrs'] = True
        return ctx

    def format_value(self, value, currency=False):
        currency_id = currency or self.env.user.company_id.currency_id
        # Change Start Here
        # WIth IFRS, need to use group curency
        if self.env.context.get('ifrs') and self.env.user.company_id.group_currency_id:
        	currency_id = self.env.user.company_id.group_currency_id
        # Change End Here
        if self.env.context.get('no_format'):
            return currency_id.round(value)
        if currency_id.is_zero(value):
            # don't print -0.0 in reports
            value = abs(value)
        res = formatLang(self.env, value, currency_obj=currency_id)
        return res
