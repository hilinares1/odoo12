# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


PARAMS = [
    ("sales_forecast_interval", str, "month"),
    ("sales_forecast_method", str, "_ar_method"),
    ("sales_predicted_periods", int, 1),
]


class res_config_settings(models.TransientModel):
    """
    Overwrite to add forecasting defaults
    """
    _inherit = "res.config.settings"

    @api.multi
    def forecast_method_selection(self):
        """
        The method to return available interval types
        """
        return [
            ("_ar_method", "Autoregression (AR)"),
            ("_ma_method", "Moving Average (MA)"),
            ("_arima_method", "Autoregressive Integrated Moving Average (ARIMA)"),
            ("_sarima_method", "Seasonal Autoregressive Integrated Moving-Average (SARIMA)"),
            ("_hwes_method", "Holt Winter’s Exponential Smoothing (HWES)"),
            ("_ses_method", "Simple Exponential Smoothing (SES)"),
        ]

    @api.multi
    def interval_selection(self):
        """
        The method to return available interval types
        """
        return [
            ("day", "Daily"),
            ("week", "Weekly"),
            ("month", "Monthly"),
            ("quarter", "Quarterly"),
            ("year", "Yearly"),
        ]

    sales_forecast_method = fields.Selection(
        forecast_method_selection,
        string="Sales Forecast method",
    )
    sales_forecast_interval = fields.Selection(
        interval_selection,
        string="Sales Data Series Interval",
    )
    sales_predicted_periods = fields.Integer(
        string="Sales Number of predicted periods",
    )

    _sql_constraints = [
        (
            'sales_predicted_periods_check',
            'check (sales_predicted_periods>0)',
            _('Number of periods should be positive ')
        ),
    ]

    @api.model
    def get_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        res = super(res_config_settings, self).get_values()
        values = {}
        for field_name, getter, default in PARAMS:
            values[field_name] = getter(str(Config.get_param(field_name, default)))
        res.update(**values)
        return res

    @api.multi
    def set_values(self):
        """
        Overwrite to add new system params
        """
        Config = self.env['ir.config_parameter'].sudo()
        super(res_config_settings, self).set_values()
        for field_name, getter, default in PARAMS:
            value = getattr(self, field_name, default)
            Config.set_param(field_name, value)
