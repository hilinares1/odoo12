from odoo import models, fields, api, _


class AdsQuantityReport(models.TransientModel):
    _name = 'calculate.average.daily.sale'
    _description = "Calculate Average Daily Sale"

    def calculate_ads(self):
        self.env['product.average.daily.sale'].calculate_average_daily_sales_using_cron()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Yeah! Average Daily sale is Calculated and updated",
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }}
