from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning
import datetime
import json
import logging

_logger = logging.getLogger(__name__)


class bank_api_wizard(models.TransientModel):
    _name = "account.bank.api.date"
    _description = 'Bank BCA API wizard'

    today = datetime.date.today()
    previous_date = today - relativedelta(months=1)
    default_start_date = datetime.date(previous_date.year, previous_date.month, 1)
    default_end_date = datetime.date(today.year, today.month, 1) - relativedelta(days=1)

    start_date = fields.Date(string='Start Date', required=True, default=default_start_date)
    end_date = fields.Date(string='End Date', required=True, default=default_end_date)

    @api.multi
    def get_bank_statement(self):
        if self.start_date > self.end_date:
            raise Warning(_('End date value is earlier than start date'))
        else:
            account_journal = self.env['account.journal'].browse(self._context.get('active_id'))
            start_date_string = self.start_date.strftime('%Y-%m-%d')
            end_date_string = self.end_date.strftime('%Y-%m-%d')
            account_journal.bank_api_id.bca_procedure_get_bank_statement(account_journal.id,account_journal.bank_account_id.acc_number,start_date_string,end_date_string)
