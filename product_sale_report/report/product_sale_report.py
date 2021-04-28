# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductSaleReport(models.Model):
    _name = 'product.sale.report'
    _description = 'Products Sale Report'
    _auto = False
    _rec_name = 'product_id'
    _order = 'product_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner', readonly=True, string='Customer')
    latitude = fields.Float(
        related='partner_id.partner_latitude', string='Latitude')
    longitude = fields.Float(
        related='partner_id.partner_longitude', string='Longitude')
    product_id = fields.Many2one(
        comodel_name='product.product', readonly=True, string='Product')
    product_category_id = fields.Many2one(
        comodel_name='product.category',
        readonly=True,
        string='Product Category')
    total_ordered = fields.Float(string='Qty Ordered')
    total_delivery = fields.Float(string='Qty Delivered')
    total_invoice = fields.Float(string='Qty Invoiced')
    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Order #',
        readonly=True)
    date = fields.Datetime(string='Order date', readonly=True)
    confirmation_date = fields.Datetime(
        string='Confirmation date',
        readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        select_ = """
            MIN(ol.id) as id,
            so.partner_id as partner_id,
            ol.product_id as product_id,
            so.id as order_id,
            so.date_order as date,
            so.state as state,
            SUM(ol.product_uom_qty) as total_ordered,
            SUM(ol.qty_delivered) as total_delivery,
            SUM(ol.qty_invoiced) as total_invoice,
            pt.categ_id as product_category_id,
            so.confirmation_date as confirmation_date
        """

        from_ = """
            sale_order_line AS ol
            JOIN product_product AS pp ON (ol.product_id = pp.id)
            JOIN sale_order AS so ON (ol.order_id = so.id)
            JOIN product_template AS pt ON (pp.product_tmpl_id = pt.id)
        """

        groupby_ = """
            ol.product_id,
            so.partner_id,
            so.id,
            pt.categ_id,
            so.date_order,
            so.confirmation_date,
            so.state
        """

        return """
            SELECT %s FROM %s WHERE ol.product_id IS NOT NULL GROUP BY %s
        """ % (select_, from_, groupby_)

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
        CREATE OR REPLACE VIEW %s AS %s
        ''' % (self._table, self._query()))
