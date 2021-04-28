""" init object fixed.asset.report.wizard """

import time
import logging
from datetime import datetime

from odoo import _, fields, models, api
from odoo.exceptions import UserError

LOGGER = logging.getLogger(__name__)


class FixedAssetReportWizard(models.TransientModel):
    """ init object fixed.asset.report.wizard """

    _name = "fixed.asset.report.wizard"
    _description = 'fixed_asset_report_wizard'

    from_date = fields.Date('From', default=time.strftime('%Y-01-01'))
    to_date = fields.Date('To', default=fields.Date.context_today)
    month = fields.Selection(
        string='Select Month',
        selection=[
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December')
        ],
        default=lambda self: str(fields.Datetime.now().month)
    )
    radio_selection = fields.Selection(
        string='Chose Report Type',
        selection=[
            ('0', 'Schedule'),
            ('1', 'Register')
        ],
        default='0', required=True)
    category_ids = fields.Many2many("account.asset.category",
                                    string="Category(s)")

    @api.multi
    def action_fixed_asset_report_search_button(self):
        """
        action_fixed_asset_report_search_button
        :return: report
        """
        self.ensure_one()
        company_id = self.env.user.company_id.id
        currency_id = self.env.user.company_id.currency_id.id
        month_search = self.month
        category = ', '.join(
            str(category_id) for category_id in self.category_ids.ids)

        from_date_search = fields.Date.to_string(self.from_date)
        to_date_search = fields.Date.to_string(self.to_date)
        radio_selection_search = self.radio_selection
        search_start_date = datetime.now()
        search_end_date = datetime.now()
        if radio_selection_search == '1':
            from_date_search = ""
            to_date_search = ""
        if not from_date_search or not to_date_search:
            if not month_search:
                raise UserError(_("Select Month."))
            search_month = month_search
            data = {'search_month': search_month,
                    'company_id': company_id,
                    'category': category,
                    'currency_id': currency_id}
            report = self.env.ref('fixed_asset_report.'
                                  'report_fixed_asset_register')
            return report.report_action([], data)
        # else case
        search_start_date = datetime.strptime(
            from_date_search, '%Y-%m-%d').strftime('%m/%d/%Y')
        search_end_date = datetime.strptime(
            to_date_search, '%Y-%m-%d').strftime('%m/%d/%Y')

        report = self.env.ref('fixed_asset_report.report_fixed_asset_schedule')
        data = {'search_start_date': search_start_date,
                'search_end_date': search_end_date,
                'company_id': company_id,
                'currency_id': currency_id,
                'category': category}
        return report.report_action([], data)
