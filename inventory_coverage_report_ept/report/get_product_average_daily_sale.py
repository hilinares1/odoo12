# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import fields, models, tools, api
from odoo.osv import expression
from odoo.tools import date_utils


class ReportAdsQuantiry(models.Model):
    _name = 'get.product.average.daily.sale'
    _auto = False
    _description = 'Get Product Average Daily Sale'

    period_start_date = fields.Date(string='Period Start Date', readonly=True)
    period_stop_date = fields.Date(String='Period Stop Date', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    period_id = fields.Many2one('requisition.period.ept', string='Period', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', readonly=True)
    monthly_sale = fields.Float('Monthly Sales', readonly=True)
    ads = fields.Float(string='ADS', readonly=True)
    type = fields.Selection([('forecasted_sales', 'Forecasted Sales'),
                             ('actual_past_sales', 'Actual Past Sales')], string='ADS Type')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'get_product_average_daily_sale')
        query = """
                    CREATE or REPLACE VIEW get_product_average_daily_sale AS (
                     Select
                        period_start_date,
                        period_stop_date,
                        product_id,
                        warehouse_id,
                        monthly_sale,
                        period_id,
                        case when avg_sale.ads < 0 then 0 else avg_sale.ads end as ads,
                        type
                    From 
                        product_average_daily_sale avg_sale
                    WHERE
                        case when (select value from ir_config_parameter where key = 'inventory_coverage_report_ept.use_forecasted_sales_for_requisition') = 'True' then 
                            period_stop_date > now()::date and type != 'actual_past_sales'
                        else
                            period_start_date >  (Select now()::date - (Select value From ir_config_parameter Where key = 'inventory_coverage_report_ept.requisition_sales_past_days')::integer) and 
                            period_start_date <= now()::date and 
                            type = 'actual_past_sales'
                        end
                    );
                    """
        self.env.cr.execute(query)
