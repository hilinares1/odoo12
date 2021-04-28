"""
 init object report.fixed_asset_report.fixed_asset_schedule_report_template
"""

import logging

from odoo import api, models

LOGGER = logging.getLogger(__name__)


class FixedAssetScheduleReportTemplate(models.AbstractModel):
    """
     init object report.fixed_asset_report.fixed_asset_schedule_report_template
    """
    _name = 'report.fixed_asset_report.fixed_asset_schedule_report_template'
    _description = 'fixed_asset_schedule_report_template Report'

    # pylint: disable=too-many-locals, sql-injection
    @api.multi
    def _get_list_data(self, search_start_date,
                       search_end_date, company_id,
                       currency_id, category):
        """
        _get_list_data
        :param search_start_date:
        :param search_end_date:
        :param company_id:
        :param currency_id:
        :param category:
        :return:
        """
        condition_for_daterange = ""
        condition_for_daterange_cost = "AND (date BETWEEN '" \
                                       + search_start_date + "' AND '" \
                                       + search_end_date + "')"
        condition_for_daterange_cost_ob = "AND (date < '" + search_start_date \
                                          + "')"
        condition_for_daterange_accumulated_depreciation = \
            "AND (line.depreciation_date BETWEEN '" + search_start_date \
            + "' AND '" + search_end_date + "')"
        condition_for_daterange_accumulated_depreciation_ob = \
            "AND (line.depreciation_date < '" + search_start_date + "')"
        condition_category = ""
        if category:
            condition_category = " AND aaa.category_id IN ( " + category + ") "

        self.env.cr.execute(
            """SELECT
        aaa.category_id
        , ( CASE
                WHEN (SELECT sum(value)
                FROM account_asset_asset
                WHERE (state = 'open' OR state = 'close')
                {cf_daterange_cost_ob}
                AND category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(value)
                FROM account_asset_asset
                WHERE (state = 'open' OR state = 'close')
                {cf_daterange_cost_ob}
                AND category_id = aaa.category_id)
            END ) AS opening_addition_cost
        , ( CASE
                WHEN (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'close' {cf_daterange_cost_ob}
                AND category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'close' {cf_daterange_cost_ob}
                AND category_id = aaa.category_id)
            END ) AS opening_disposal_cost
        , ( CASE
                WHEN (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'open' {cf_daterange_cost_ob}
                AND category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'open' {cf_daterange_cost_ob}
                AND category_id = aaa.category_id)
            END ) AS opening_balance_cost
        , ( CASE
                WHEN (SELECT sum(value)
                FROM account_asset_asset
                WHERE (state = 'open' OR state = 'close')
                {condition_for_daterange_cost}
                AND category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(value)
                FROM account_asset_asset
                WHERE (state = 'open' OR state = 'close')
                {condition_for_daterange_cost}
                AND category_id = aaa.category_id)
            END ) AS addition_cost
        , ( CASE
                WHEN (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'close' {condition_for_daterange_cost}
                AND category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(value)
                FROM account_asset_asset
                WHERE state = 'close' {condition_for_daterange_cost}
                AND category_id = aaa.category_id)
            END ) AS disposal_cost
        , ( CASE
                WHEN (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                LEFT JOIN
                account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open'
                AND line.move_posted_check = true {cfdad_ob}
                AND asset.category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open'
                AND line.move_posted_check = true {cfdad_ob}
                AND asset.category_id = aaa.category_id)
            END ) AS opening_balance_accumulated_depreciation
        , ( CASE
                WHEN (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open' AND line.move_posted_check = true
                {cfdad}
                AND asset.category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'open' AND line.move_posted_check = true
                {cfdad}
                AND asset.category_id = aaa.category_id)
            END ) AS depreciation_accumulated_depreciation
        , ( CASE
                WHEN (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                 LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
                 WHERE asset.state = 'close'
                 AND line.move_posted_check = true {cfdad}
                 AND asset.category_id = aaa.category_id) IS NULL THEN '0'
                ELSE (SELECT sum(line.amount)
                FROM account_asset_depreciation_line line
                LEFT JOIN account_asset_asset asset ON line.asset_id = asset.id
                WHERE asset.state = 'close'
                AND line.move_posted_check = true {cfdad}
                AND asset.category_id = aaa.category_id)
            END ) AS disposal_accumulated_depreciation
        FROM account_asset_asset aaa
        WHERE aaa.company_id = %s 
        {condition_category}
        {condition_for_daterange}
        GROUP BY aaa.category_id;
        """.format(cf_daterange_cost_ob=condition_for_daterange_cost_ob,
                   condition_for_daterange_cost=condition_for_daterange_cost,
                   cfdad_ob=condition_for_daterange_accumulated_depreciation_ob,
                   cfdad=condition_for_daterange_accumulated_depreciation,
                   condition_category=condition_category,
                   condition_for_daterange=condition_for_daterange),
            (tuple(str(company_id)),)
        )
        res = self.env.cr.dictfetchall()
        list_data = []
        for item in res:
            item_closing_balance_cost = (float(
                item['opening_balance_cost']) + float(
                item['addition_cost'])) - float(item['disposal_cost'])
            itm1 = float(item['opening_balance_accumulated_depreciation'])
            itm2 = float(item['depreciation_accumulated_depreciation'])
            itm3 = float(item['disposal_accumulated_depreciation'])
            item_closing_balance_accumulated_depreciation = itm1 + itm2 - itm3
            it_cl_bal_acc_dep = item_closing_balance_accumulated_depreciation
            item_net_book = item_closing_balance_cost - it_cl_bal_acc_dep
            category_id = self.env['account.asset.category'].browse(
                item['category_id'])
            list_data.append({
                'category_id': category_id,
                'currency_id': currency_id,
                'search_start_date': search_start_date,
                'search_end_date': search_end_date,
                'opening_addition_cost': item['opening_addition_cost'],
                'opening_disposal_cost': item['opening_disposal_cost'],
                'opening_balance_cost': item['opening_balance_cost'],
                'addition_cost': item['addition_cost'],
                'disposal_cost': item['disposal_cost'],
                'closing_balance_cost': item_closing_balance_cost,

                'opening_balance_accumulated_depreciation': item[
                    'opening_balance_accumulated_depreciation'],
                'depreciation_accumulated_depreciation': item[
                    'depreciation_accumulated_depreciation'],
                'disposal_accumulated_depreciation': item[
                    'disposal_accumulated_depreciation'],
                'closing_balance_accumulated_depreciation':
                    item_closing_balance_accumulated_depreciation,
                'net_book': item_net_book
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
            'fixed_asset_report.report_fixed_asset_schedule')
        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'company': self.env['res.company'].browse(data['company_id']),
            'docs': self.env.user,
            'doc': self.env.user,
            'o': self.env.user,
            'list_data': self._get_list_data(data['search_start_date'],
                                             data['search_end_date'],
                                             data['company_id'],
                                             data['currency_id'],
                                             data['category']),
        }
