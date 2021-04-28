# -*- coding: utf-8 -*-

import base64
import logging
import tempfile

from calendar import monthcalendar
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except:
    raise UserError(_("The python library 'pandas' is not installed"))
try:
    import statsmodels.tsa as tsa
except:
    raise UserError(_("The python library 'statsmodels' is not installed"))
try:
    import xlsxwriter
except ImportError:
    raise UserError(_("The python library 'xlsxwriter' is not installed"))


class open_sales_series(models.TransientModel):
    """
    The model to prepare stock demand by date and forecast trend

    Used materials:
     * https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3
     * https://people.duke.edu/~rnau/411arim.htm
     * https://machinelearningmastery.com/time-series-forecasting-methods-in-python-cheat-sheet/
    """
    _name = 'open.sales.series'
    _description = 'Calculate trend and forecast'

    @api.multi
    def interval_selection(self):
        """
        The method to return available interval types
        """
        return self.env['res.config.settings'].sudo().interval_selection()

    @api.multi
    def forecast_method_selection(self):
        """
        The method to return available forecast methods
        """
        return self.env['res.config.settings'].sudo().forecast_method_selection()

    @api.model
    def default_predicted_periods(self):
        """
        Default method for predicted_periods
        """
        return int(self.env['ir.config_parameter'].sudo().get_param("sales_predicted_periods", 1))

    @api.model
    def default_interval(self):
        """
        Default method for interval
        """
        return self.env['ir.config_parameter'].sudo().get_param("sales_forecast_interval", "month")

    @api.model
    def default_forecast_method(self):
        """
        Default method for forecast_method
        """
        return self.env['ir.config_parameter'].sudo().get_param("sales_forecast_method", "_ar_method")

    @api.multi
    @api.onchange("interval")
    def _onchange_interval(self):
        """
        Onchange method for interval to pass the last dare of the previous period

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        today = fields.Date.from_string(fields.Date.today())
        res_date = today
        interval = self.interval
        if interval == "day":
            res_date = today - relativedelta(days=1)
            seasons = 7
        elif interval == "week":
            res_date = today - relativedelta(days=today.weekday() + 1)
            seasons = 1
        elif interval == "month":
            last_month_date = today - relativedelta(months=1)
            res_date = date(
                year=last_month_date.year,
                month=last_month_date.month,
                day=monthrange(last_month_date.year, last_month_date.month)[1],
            )
            seasons = 3
        elif interval == "quarter":
            last_quarter_date = today - relativedelta(months=3)
            last_quarter_month = int(3 * (int((last_quarter_date.month - 1)) / 3  + 1))
            res_date = date(
                year=last_quarter_date.year,
                month=last_quarter_month,
                day=monthrange(last_quarter_date.year, last_quarter_month)[1],
            )
            seasons = 2
        elif interval == "year":
            last_year_date = today - relativedelta(years=1)
            res_date = date(
                year=last_year_date.year,
                month=12,
                day=monthrange(last_year_date.year, 12)[1],
            )
            seasons = 1
        self.date_end = res_date
        self.seasons = seasons

    @api.multi
    @api.onchange("forecast_method")
    def _onchange_forecast_method(self):
        """
        Onchange method for forecast

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if self.forecast_method in ["_hwes_method", "_ses_method"]:
            predicted_periods = 1
        else:
            predicted_periods = int(self.env['ir.config_parameter'].sudo().get_param("sales_predicted_periods", 1))
        self.predicted_periods = predicted_periods

    product_ids = fields.Many2many(
        "product.product",
        string="Products"
    )
    template_ids = fields.Many2many(
        "product.template",
        string="Product Templates",
    )
    category_ids = fields.Many2many(
        "product.category",
        string="Product Categories"
    )
    team_ids = fields.Many2many(
        "crm.team",
        string="Sales Teams",
        help="If not selected all teams would be taken into account",
    )
    country_id = fields.Many2one(
        'res.country',
        'Partner Country',
        help="If not selected all countries would be taken into account",
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Salespersons",
        help="If not selected all sales persons would be taken into account",
    )
    date_start = fields.Date(
        string="Data Series",
        help="""
        Using Data Series Start and End you indicate which historical data is used for prediction
        If no defined, all historical data would be used, including one from a current period
        """,
    )
    date_end = fields.Date(
        string="Data Series End",
    )
    predicted_periods = fields.Integer(
        string="Number of predicted periods",
        default=default_predicted_periods,
    )
    interval = fields.Selection(
        interval_selection,
        string="Data Series Interval",
        default=default_interval,
    )
    forecast_method = fields.Selection(
        forecast_method_selection,
        string="Forecast method",
        default=default_forecast_method,
    )
    seasons = fields.Integer(
        string="Seasons",
        default=1
    )
    p_coefficient = fields.Integer(
        string="P coefficient (auto regressive)",
        default=1,
    )
    d_coefficient = fields.Integer(
        string="D coefficient (integrated)",
        default=1,
    )
    q_coefficient = fields.Integer(
        string="Q coefficient (moving average)",
        default=1,
    )
    seasonal_p_coefficient = fields.Integer(
        string="Seasonal P coefficient (auto regressive)",
        default=1,
    )
    seasonal_d_coefficient = fields.Integer(
        string="Seasonal D coefficient (integrated)",
        default=1,
    )
    seasonal_q_coefficient = fields.Integer(
        string="Seasonal Q coefficient (moving average)",
        default=1,
    )

    _sql_constraints = [
        (
            'predicted_periods_check',
            'check (predicted_periods>0)',
            _('Number of periods should be positive ')
        ),
        (
            'dates_check',
            'check (date_end>date_start)',
            _('Date end should be after date start')
        ),
    ]

    @api.multi
    def action_calculate(self):
        """
        The method to open odoo report with current and forecast time series

        Methods:
         * _calculate_data

        Extra info:
         * Expected singleton

        To-do:
         * Think of improving performace trhrough explcit iniating the model instead of multi create
        """
        self.ensure_one()
        sales = self._calculate_data()
        demands = self.env["report.sale.forecast.periods"].create(sales)
        action = self.env.ref("sales_forecast_by_periods.report_sale_forecast_periods_action").read()[0]
        action["domain"] = [('id', 'in', demands.ids)]
        interval = self.interval
        ctx = interval == 'day' and {"search_default_day" : 1} \
              or interval == 'week' and {"search_default_week" : 1} \
              or interval == 'month' and {"search_default_month" : 1} \
              or interval == 'quarter' and {"search_default_quarter" : 1} \
              or {"search_default_year" : 1}
        action["context"] = ctx
        return action

    @api.multi
    def action_export_to_xlsx(self):
        """
        The method to prepare an xlsx table of data series

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like 'A' or 'S' (ascii char depends on counter)
        3. Make a line from each data period
        4. Create and upload an attachment

        Methods:
         * _calculate_data

        Returns:
         * action of downloading the xlsx table

        Extra info:
         * Expected singleton

        To-do:
         * think of better name for the report
        """
        self.ensure_one()
        xlsx_name = u"{}#{}.xlsx".format(self.forecast_method, fields.Date.today())
        # 1
        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = {
            'main_header_style': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'border': 1,
            }),
            'main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
            }),
            'red_main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
                'font_color': 'blue',
            }),
            'data_time_format': workbook.add_format({
                'font_size': 11,
                'border': 1,
                'num_format': 'yy/mm/dd',
            }),
            'red_data_time_format': workbook.add_format({
                'font_size': 11,
                'border': 1,
                'num_format': 'yy/mm/dd',
                'font_color': 'blue',
            }),
        }
        worksheet = workbook.add_worksheet(xlsx_name)

        # 2
        cur_column = 0
        for column in [_("Date"), _("Sales")]:
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            column_width = 20
            worksheet.set_column('{c}:{c}'.format(c=col_letter), column_width)
            cur_column += 1
        # 3
        sales = self._calculate_data()
        sales = sorted(sales, key=lambda k: k['date_datetime'], reverse=True)
        row = 1
        for sale in sales:
            red = sale.get("forecast") and "red_" or ""
            instance = (
                sale.get("date_datetime"),
                sale.get("quantity"),
            )
            for counter, column in enumerate(instance):
                value = column
                worksheet.write(
                    row,
                    counter,
                    value,
                    counter == 0 and styles.get(red+"data_time_format") or styles.get(red+"main_data_style")
                )
            row += 1
        workbook.close()
        # 4
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name':  xlsx_name,
            'type': 'binary',
            'datas': xls_file,
            'datas_fname': xlsx_name,
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id,),
            'target': 'self',
        }
        return action

    @api.multi
    def _calculate_data(self):
        """
        The method to calculate data series + forecast

        1. Fetch all sale order lines grouped by interval from SQL
        2. Make pandas dataframe and fill in missing values
        3. Apply related forecast method to get predicted values if possible
        4. Make single list of dicts of stock demands

        Methods:
         * _build_dynamic_clause

        Returns:
         * list of dicts:
          ** date
          ** quantity
          ** whether it is forecast

        Extra info:
         * Expected singleton

        To-do:
         * think of price_total vs price_subtotal
        """
        self.ensure_one()
        where_clause, with_clause  = self._build_dynamic_clause()
        interval = self.interval
        freq = interval[0]
        # 1
        query = with_clause + """
            SELECT
                DATE_TRUNC(%(interval)s, so.date_order) as date_gr,
                SUM((sol.price_total / CASE COALESCE(so.currency_rate, 0) WHEN 0 THEN 1.0 ELSE so.currency_rate END))
                     AS qty
            FROM sale_order_line sol
                 JOIN sale_order so ON (sol.order_id = so.id)
                 LEFT JOIN product_product pro ON (sol.product_id = pro.id)
                 LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                 JOIN res_partner rp ON (so.partner_id = rp.id)
            WHERE
                (so.state = 'done' OR so.state = 'sale')
                AND so.company_id = %(company_id)s
        """ + where_clause + \
        """
            GROUP BY date_gr
            ORDER BY date_gr
        """
        options = {
            "interval": interval,
            "product_ids": self.product_ids.ids,
            "template_ids": self.template_ids.ids,
            "category_ids": self.category_ids.ids,
            "team_ids": self.team_ids.ids,
            "user_ids": self.user_ids.ids,
            "country_id": self.country_id.id,
            "date_start": self.date_start,
            "date_end": self.date_end,
            "company_id": self.env.user.company_id.id,
        }
        self._cr.execute(query, options)
        sales = self._cr.dictfetchall()
        # 2
        if not sales:
            raise UserError(_("No historical data is defined for the specified period"))
        if self.date_start and sales[0].get("date_gr") > fields.Datetime.from_string(self.date_start):
            sales.append({"date_gr": fields.Datetime.from_string(self.date_start), "qty": 0.0})
        if self.date_end and sales[-1].get("date_gr") < fields.Datetime.from_string(self.date_end):
            sales.append({"date_gr": fields.Datetime.from_string(self.date_end), "qty": 0.0})

        sales_table = pd.DataFrame(sales, columns=['date_gr', "qty"])
        sales_table.set_index(sales_table.date_gr, inplace=True)
        sales_table = sales_table.resample(freq).sum().fillna(0.0)
        # 3
        method_to_call = getattr(self, self.forecast_method)
        forecast = method_to_call(sales_table)
        # 4
        res_sales = [{"date_datetime": key.date(), "quantity": value} \
                     for key, value in sales_table.to_dict().get("qty").items()]
        if type(forecast) != bool:
            forecast_sales = [{
                                "date_datetime": key.date(),
                                "quantity": value > 0 and round(value, 2) or 0.0,
                                "forecast": True
                              } \
                              for key, value in forecast.to_dict().items()]
            res_sales += forecast_sales
        return res_sales

    @api.multi
    def _build_dynamic_clause(self):
        """
        The method to build where for sql statement (by date, locations) and with as helpers for where
        #  based on used data series

        Returns:
         * str, str (both are sql query without params)

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        where_clause = ""
        with_clause = ""
        #
        if self.product_ids:
            where_clause += """
                AND sol.product_id = ANY(%(product_ids)s)
            """
        if self.template_ids:
            where_clause += """
                AND pro.product_tmpl_id = ANY(%(template_ids)s)
            """
        if self.category_ids:
            with_clause = """
                WITH RECURSIVE all_categories AS(
                SELECT id, parent_id
                FROM product_category
                WHERE (parent_id = ANY(%(category_ids)s) OR id = ANY(%(category_ids)s))
                UNION
                SELECT product_category.id, product_category.parent_id
                FROM product_category
                    JOIN all_categories
                        ON product_category.parent_id = all_categories.id
                )
            """
            where_clause += """
                AND pt.categ_id IN (SELECT id FROM all_categories)
            """
        if self.team_ids:
            where_clause += """
                AND so.team_id = ANY(%(team_ids)s)
            """
        if self.user_ids:
            where_clause += """
                AND so.user_id = ANY(%(user_ids)s)
            """
        if self.country_id:
            where_clause += """
                AND rp.country_id <= %(country_id)s
            """
        if self.date_start:
            where_clause += """
                AND so.date_order::date >= %(date_start)s
            """
        if self.date_end:
            where_clause += """
                AND so.date_order::date <= %(date_end)s
            """
        return where_clause, with_clause

    @api.multi
    def _ar_method(self, data):
        """
        The method to reveal a trend as autoregression

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.ar_model import AR
            model = AR(data)
            model_fit = model.fit()
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1)
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction

    @api.multi
    def _ma_method(self, data):
        """
        The method to reveal a trend as moving average

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.arima_model import ARMA
            model = ARMA(data, order=(self.p_coefficient, self.d_coefficient))
            model_fit = model.fit(disp=False)
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1)
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction

    @api.multi
    def _arima_method(self, data):
        """
        The method to reveal a trend as auto regressive integrated moving average

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.arima_model import ARIMA
            model = ARIMA(data, order=(self.p_coefficient, self.d_coefficient, self.q_coefficient))
            model_fit = model.fit(disp=False)
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1, typ='levels')
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction

    @api.multi
    def _sarima_method(self, data):
        """
        The method to reveal a trend as seasonal auto regressive integrated moving average

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            model = SARIMAX(
                data,
                order=(self.p_coefficient, self.d_coefficient, self.q_coefficient),
                seasonal_order=(
                    self.seasonal_p_coefficient,
                    self.seasonal_d_coefficient,
                    self.seasonal_q_coefficient, self.seasons
                )
            )
            model_fit = model.fit(disp=False)
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1)
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction

    @api.multi
    def _hwes_method(self, data):
        """
        The method to reveal a trend as Holt Winter’s Exponential Smoothing

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            model = ExponentialSmoothing(data)
            model_fit = model.fit()
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1)
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction

    @api.multi
    def _ses_method(self, data):
        """
        The method to reveal a trend as Simple Exponential Smoothing (SES)

        Args:
         * data - pd series

        Returns:
         * predicted series or False if data is not sufficient

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        try:
            from statsmodels.tsa.holtwinters import SimpleExpSmoothing
            model = SimpleExpSmoothing(data)
            model_fit = model.fit()
            prediction = model_fit.predict(start=len(data), end=len(data)+self.predicted_periods-1)
        except Exception as er:
            _logger.warning(u"The data is not sufficient to make prediction. Error: {}".format(er))
            prediction = False
        return prediction
