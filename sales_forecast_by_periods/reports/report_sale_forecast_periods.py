# -*- coding: utf-8 -*-


from odoo import fields, models

class report_sale_forecast_periods(models.TransientModel):
    """
    The model to reflect real and forecast sales time series
    """
    _name = 'report.sale.forecast.periods'
    _description = 'Sales Forecast'

    date_datetime = fields.Date(string="Sales Period")
    quantity = fields.Float(string="Sales", readonly=True)
    forecast = fields.Boolean(string="Forecast", readonly=True)
