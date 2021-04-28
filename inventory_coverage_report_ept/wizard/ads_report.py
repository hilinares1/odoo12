from odoo import models, fields, api, _

class AdsQuantityReport(models.TransientModel):
    _name = 'ads.quantity.report'
    _description = "ADS quantity report"

    def default_warehouse_ids(self):
        warehouses = self.env['stock.warehouse'].search([]).filtered(lambda x: x.company_id.id == self.env.user.company_id.id)
        return warehouses

    product_ids = fields.Many2many('product.product', string='Products',
                                   help="Select products for selected products wise filter report")
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse', default=default_warehouse_ids,
                                     help="Select multiple warehouse for filter warehouse wise")


    def display_report(self):
        """
        Pass warehouses and products wise filter for report filter.
        @author: Harsh Parekh 15 Jan, 2020
        :return: pivot view with default filter
        """

        product_average_daily_sale_report_obj = self.env['product.average.daily.sale.report']

        product_ids = self.product_ids
        if not product_ids:
            product_ids = self.env['product.product'].search([('type','=','product')])

        warehouse_ids = self.warehouse_ids
        if not warehouse_ids:
            warehouse_ids = self.env['stock.warehouse'].search([]).filtered(lambda x: x.company_id.id == self.env.user.company_id.id)

        product_average_daily_sale_report_obj.with_context({'warehouse_ids':warehouse_ids.ids or [0],'product_ids':product_ids.ids or []}).init()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Average Daily Sales Report',
            'res_model': 'product.average.daily.sale.report',
            'view_mode': 'pivot',
            'context': {
                'search_default_last_3_month': 1,
            },
        }
