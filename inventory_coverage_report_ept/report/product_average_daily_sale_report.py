# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, tools, api
from odoo import tools


class ProductAdsReport(models.Model):
    _name = 'product.average.daily.sale.report'
    _description = 'Get Product Average Daily Sale Report'
    _auto = False

    period_start_date = fields.Date(string='Period Start Date', readonly=True)
    period_stop_date = fields.Date(String='Period Stop Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    period_id = fields.Many2one('requisition.period.ept', string='Period', readonly=True)
    ads = fields.Float(string='Average Daily Sale', readonly=True)
    monthly_sale = fields.Float('Monthly Sales', readonly=True)
    warehouse_code = fields.Char("Warehouse Code", readonly=True)
    type = fields.Selection([('forecasted_sales', 'Forecasted Sales'),
                             ('actual_past_sales', 'Actual Past Sales')], string='ADS Type',
                            readonly=True)

    def init(self):
        """
        @author: Harsh Parekh 15 Jan, 2020
        :return: report data in pivot view based on warehouse and product selection and drop view if already exist then.
        """
        context = dict(self._context) or {}
        product_ids = context.get('product_ids') or []
        warehouse_ids = context.get('warehouse_ids') or []
        product_list = '(' + str(product_ids).strip('[]') + ')'
        warehouse_list = '(' + str(warehouse_ids).strip('[]') + ')'
        tools.drop_view_if_exists(self._cr, 'product_average_daily_sale_report')
        where_clause = ""
        if product_ids:
            where_clause += """product_id IN %s AND """ % product_list
        if warehouse_ids:
            where_clause += """warehouse_id IN %s AND """ % warehouse_list
        query = """
                    CREATE or REPLACE VIEW product_average_daily_sale_report AS (
                     Select
                        id,
                        period_start_date,
                        period_stop_date,
                        product_id,
                        period_id,
                        ads,
                        monthly_sale,
                        sw.code as warehouse_code,                        
                        type
                    From
                        get_product_average_daily_sale as get_product_avg_sale
                         INNER JOIN stock_warehouse sw on sw.id = get_product_avg_sale.warehouse_id
                    WHERE
                    %s
                    type='actual_past_sales'
                    );
                    """ % where_clause
        self._cr.execute(query)
