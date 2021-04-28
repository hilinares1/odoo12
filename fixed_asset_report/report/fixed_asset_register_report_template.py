"""
init object report.fixed_asset_report.fixed_asset_register_report_template
"""
import logging
from datetime import datetime

import calendar
from odoo import api, models

LOGGER = logging.getLogger(__name__)


class FixedAssetRegisterReportTemplate(models.AbstractModel):
    """
    init object report.fixed_asset_report.fixed_asset_register_report_template
    """
    _name = 'report.fixed_asset_report.fixed_asset_register_report_template'
    _description = 'fixed_asset_register_report_template Report'

    # pylint: disable=too-many-locals, sql-injection
    @api.multi
    def _get_list_data(self, search_month, company_id, currency_id, category):
        """
        _get_list_data
        :param search_month:
        :param company_id:
        :param currency_id:
        :param category:
        :return:
        """
        now = datetime.now().date()
        days = calendar.monthrange(now.year, int(search_month))[1]
        search_start_date = datetime(now.year, int(search_month),
                                     1).date().strftime('%Y-%m-%d')
        search_end_date = datetime(now.year, int(search_month),
                                   days).date().strftime('%Y-%m-%d')
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'Setember', 'October', 'November',
                  'December']
        month_name = months[int(search_month) - 1]
        month_name = month_name.capitalize()
        condition_for_daterange = "AND (aadl.depreciation_date BETWEEN '" \
                                  + search_start_date + "' AND '" \
                                  + search_end_date + "')"
        condition_for_daterange_line = "AND (line.depreciation_date BETWEEN '" \
                                       + search_start_date + "' AND '" \
                                       + search_end_date + "')"
        condition_category = ""
        if category:
            condition_category = " AND aaa.category_id IN ( " + category + ") "

        self.env.cr.execute(
            """SELECT
        aac.id AS category_id
        , aaa.id AS asset_id
        , aaa.asset_code
        , aaa.name AS asset_name
        , aaa.manufacturer
        , aaa.serial_number
        , aaa.model_number
        , aaa.date AS purchase_date
        , aaa.value AS cost
        , ( CASE
                WHEN (SELECT sum(line.depreciated_value)
                FROM account_asset_depreciation_line line
                LEFT JOIN
                account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open' {condition_daterange_line}
                AND asset.id = aaa.id) IS NULL THEN '0'
                ELSE (SELECT sum(line.depreciated_value)
                FROM account_asset_depreciation_line line
                LEFT JOIN
                account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open' {condition_daterange_line}
                AND asset.id = aaa.id)
        END ) AS accumulated_depreciation
        , ( CASE
            WHEN (SELECT sum(line.remaining_value)
            FROM account_asset_depreciation_line line
            LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
            WHERE asset.state = 'open' {condition_daterange_line}
            AND asset.id = aaa.id) IS NULL THEN '0'
            ELSE (SELECT sum(line.remaining_value)
            FROM account_asset_depreciation_line line
            LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
            WHERE asset.state = 'open' {condition_daterange_line}
            AND asset.id = aaa.id)
        END ) AS net_book
        , aaa.currency_id
        , aaa.company_id
        FROM account_asset_depreciation_line aadl
        LEFT JOIN account_asset_asset aaa ON aadl.asset_id = aaa.id
        LEFT JOIN account_asset_category aac ON aaa.category_id = aac.id
        WHERE aaa.company_id = %s
        {condition_for_daterange}
        {condition_category}
        
        GROUP BY aaa.id
            , aac.id
            , aaa.asset_code
            , aaa.name
            , aaa.manufacturer
            , aaa.serial_number
            , aaa.model_number
            , aaa.date
            , aaa.currency_id
            , aaa.company_id;
            """.format(
                condition_daterange_line=condition_for_daterange_line,
                condition_category=condition_category,
                condition_for_daterange=condition_for_daterange
            ), (tuple(str(company_id)))
        )
        res = self.env.cr.dictfetchall()
        list_data = []
        for item in res:
            category_id = self.env['account.asset.category'].browse(
                item['category_id'])
            asset_id = self.env['account.asset.asset'].browse(
                item['asset_id'])
            purchase_date_str = item['purchase_date'].strftime('%d/%m/%Y')
            list_data.append({
                'category_id': category_id,
                'asset_id': asset_id,
                'asset_code': item['asset_code'],
                'asset_name': item['asset_name'],
                'manufacturer': item['manufacturer'],
                'serial_number': item['serial_number'],
                'model_number': item['model_number'],
                'purchase_date': purchase_date_str,
                'cost': item['cost'],
                'accumulated_depreciation': item['accumulated_depreciation'],
                'net_book': item['net_book'],
                'month': month_name,
                'currency_id': currency_id
            })
        return list_data

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Override report values.
        :param docids:
        :param data:
        :return:
        """
        # pylint: disable=protected-access
        report = self.env['ir.actions.report']._get_report_from_name(
            'fixed_asset_report.report_fixed_asset_register ')
        fields_get = self.env['fixed.asset.report.wizard'].fields_get(
            allfields=['month'])
        month_selected = dict(fields_get['month']['selection'])[
            data['search_month']]
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'company': self.env['res.company'].browse(data['company_id']),
            'currency_id': self.env['res.company'].browse(data['currency_id']),
            'docs': self.env.user,
            'doc': self.env.user,
            'o': self.env.user,
            'month_selected': month_selected,
            'list_data': self._get_list_data(data['search_month'],
                                             data['company_id'],
                                             data['currency_id'],
                                             data['category']),
        }
