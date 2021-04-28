# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
#========For Excel========
from io import BytesIO
import xlwt
from xlwt import easyxf
import base64
# =====================

class inventory_wizard(models.TransientModel):
    _name = 'inventory.age.wizard'
    
    date_from = fields.Date('Date', required="1", default=fields.Date.today)
    company_id = fields.Many2one('res.company', string='Company', required="1", default=lambda self:self.env.user.company_id.id)
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouse', required="1", default=lambda self: self.env['stock.warehouse'].search([], limit=1))
    location_ids = fields.Many2one('stock.location', string='Locations')
    period_length = fields.Selection([('Daily','Daily'),('Weekly','Weekly'),('Monthly','Monthly'),('Yearly','Yearly')],string='Period', default='Daily', required="1")
    filter_by = fields.Selection([('by_product','Product'),('by_category','Product Category')], string='Filter By', default="by_category")
    product_ids = fields.Many2many('product.product', string='Product', domain=[('type','=','product')])
    category_id = fields.Many2one('product.category', string='Product Category', default=lambda self: self.env['product.category'].search([("name","=","Raw Product")], limit=1))
    excel_file = fields.Binary('Excel File')
    
    # Style of Excel Sheet     
    #==============================
    main_header_style = easyxf('font:height 300;align: vert centre;')
    header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;align: vert centre, horiz center;font: color black; font:bold True;borders: top thin,left thin,right thin,bottom thin')
    left_header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;align: horiz left;font: color black; font:bold True;borders: top thin,left thin,right thin,bottom thin')
    text_left = easyxf('font:height 200; align: horiz left;')
    text_right = easyxf('font:height 200; align: horiz right;', num_format_str='0.000')
    text_left_bold = easyxf('font:height 200; align: horiz right;font:bold True;')
    text_right_bold = easyxf('font:height 200; align: horiz right;font:bold True;', num_format_str='0.000') 
    text_center = easyxf('font:height 200; align: horiz center;')  

    text_left_border = easyxf('font:height 200; align: horiz left;borders: top thin,left thin,right thin,bottom thin;')
    text_right_border = easyxf('font:height 200; align: horiz right;borders: top thin,left thin,right thin,bottom thin;', num_format_str='0.000')
    text_left_bold_border = easyxf('font:height 200; align: horiz right;font:bold True;borders: top thin,left thin,right thin,bottom thin;')
    text_right_bold_border = easyxf('font:height 200; align: horiz right;font:bold True;borders: top thin,left thin,right thin,bottom thin;', num_format_str='0.000') 
    text_center_border = easyxf('font:height 200; align: horiz center;borders: top thin,left thin,right thin,bottom thin;')  
    #==============================  

    @api.multi
    def get_products(self):
        product_pool=self.env['product.product']
        if not self.filter_by:
            return product_pool.search([('type','=','product')])
        else:
            if self.filter_by == 'by_product':
                if self.product_ids:
                    return self.product_ids
            else:
                product_ids = product_pool.search([('categ_id','child_of',self.category_id.id),('type','=','product')])
                if product_ids:
                    return product_ids
                else:
                    raise ValidationError("Product not found in selected category !!!")
                   
    @api.multi
    def create_excel_header(self,worksheet):
        worksheet.write_merge(0, 1, 0, 2, 'Stock Inventory Aging', self.main_header_style)
        row = 3
        col=0
        worksheet.write(row,col, 'Period Length', self.left_header_style)
        worksheet.write(row,col+1, self.period_length, self.text_left)
        row+=1
        worksheet.write(row,col, 'Date From', self.left_header_style)
        date = datetime.strftime(self.date_from, "%d-%m-%Y")
        worksheet.write(row,col+1, date, self.text_left)
        row+=1
        worksheet.write(row,col, 'Company', self.left_header_style)
        worksheet.write(row,col+1, self.company_id.name or '', self.text_left)
        row+=1
        worksheet.write(row,col, 'Warehouse', self.left_header_style)
        ware_name = ', '.join(map(lambda x: (x.name), self.warehouse_ids))
        worksheet.write(row,col+1,ware_name or '', self.text_left)
        if self.filter_by:
            row+=1
            worksheet.write(row,col, 'Filter By', self.left_header_style)
            if self.filter_by == 'by_product':
                worksheet.write(row,col+1, 'Products', self.text_left)
            else:
                worksheet.write(row,col+1, 'Product Category' + ':' + self.category_id.name or '', self.text_left)

        # if self.filter_by and self.filter_by == 'by_category':                
        #     row+=1
        #     worksheet.write(row,col+1, 'Product Category', self.left_header_style)
        #     worksheet.write_merge(row,row, col+4, col+5, self.category_id.name or '', self.text_left)

        if self.location_ids:
            row+=1
            worksheet.write(row,col, 'Location', self.left_header_style)
            location_name = ', '.join(map(lambda x: (x.name), self.location_ids))
            worksheet.write_merge(row,row, col+1, col+3, location_name or '', self.text_left)
            
        row+=1
        return worksheet, row
        
        
    @api.multi
    def create_table_header(self,worksheet,row,res):
        worksheet.write_merge(row, row+1, 0, 0, 'Code', self.header_style)
        worksheet.write_merge(row,row+1, 1, 1, 'Product', self.header_style)
        worksheet.write_merge(row,row+1, 2, 2, 'Unit', self.header_style)
        worksheet.write_merge(row,row+1, 3, 3, 'Total Qty', self.header_style)
        worksheet.write_merge(row,row+1, 4, 4, 'Total Value', self.header_style)

        worksheet.write_merge(row,row, 5, 6, res['6']['name'], self.header_style)
        worksheet.write(row+1, 5, 'Qunatity', self.header_style)
        worksheet.write(row+1, 6, 'Value', self.header_style)
        worksheet.write_merge(row,row, 7, 8, res['5']['name'], self.header_style)
        worksheet.write(row+1, 7, 'Qunatity', self.header_style)
        worksheet.write(row+1, 8, 'Value', self.header_style)
        worksheet.write_merge(row,row, 9, 10, res['4']['name'], self.header_style)
        worksheet.write(row+1, 9, 'Qunatity', self.header_style)
        worksheet.write(row+1, 10, 'Value', self.header_style)
        worksheet.write_merge(row,row, 11, 12, res['3']['name'], self.header_style)
        worksheet.write(row+1, 11, 'Qunatity', self.header_style)
        worksheet.write(row+1, 12, 'Value', self.header_style)
        worksheet.write_merge(row,row, 13, 14, res['2']['name'], self.header_style)
        worksheet.write(row+1, 13, 'Qunatity', self.header_style)
        worksheet.write(row+1, 14, 'Value', self.header_style)
        worksheet.write_merge(row,row, 15, 16, res['1']['name'], self.header_style)
        worksheet.write(row+1, 15, 'Qunatity', self.header_style)
        worksheet.write(row+1, 16, 'Value', self.header_style)
        worksheet.write_merge(row,row, 17, 18, res['0']['name'], self.header_style)
        worksheet.write(row+1, 17, 'Qunatity', self.header_style)
        worksheet.write(row+1, 18, 'Value', self.header_style)
        row+=1
        return worksheet, row
    
    @api.multi
    def get_aging_quantity(self,product,to_date=False):
        if to_date:
            product = product.with_context(to_date=to_date)
        if self.warehouse_ids:
            product = product.with_context(warehouse=self.warehouse_ids.ids)
        if self.location_ids:
            product = product.with_context(location=self.location_ids.ids)

        return product.qty_available
    
    @api.multi
    def create_table_values(self,worksheet,row,res,product_ids):
        lst=[0,0,0,0,0,0,0]
        lst_val=[0,0,0,0,0,0,0]
        row = row+1
        total_qty = total_val=0
        for product in product_ids:
            worksheet.write_merge(row,row, 0, 0, product.barcode or '', self.text_left_border)
            worksheet.write_merge(row,row, 1, 1, product.name, self.text_left_border)
            worksheet.write_merge(row,row, 2, 2, product.uom_name, self.text_left_border)
            stock_qty = self.get_aging_quantity(product,self.date_from)
            total_qty += stock_qty
            total_val += stock_qty * product.standard_price
            worksheet.write(row, 3, stock_qty, self.text_right_border)
            worksheet.write(row, 4,stock_qty * product.standard_price, self.text_right_border)
            col=5
            for i in range(7)[::-1]:
                from_qty = to_qty = 0
                from_qty = self.get_aging_quantity(product,res[str(i)]['stop'])
                if res[str(i)]['start']:
                    to_qty = self.get_aging_quantity(product,res[str(i)]['start'])
                qty = from_qty - to_qty
                lst[i] += qty
                lst_val[i] += qty * product.standard_price
                worksheet.write(row,col, qty or 0, self.text_right_border)
                col+=1
                worksheet.write(row,col, qty * product.standard_price or 0, self.text_right_border)
                col+=1
            row+=1
#        
##        worksheet.write_merge(row,row, 0, 2, 'TOTAL', self.text_right_bold)
        worksheet.write_merge(row,row, 0, 2, 'TOTAL', self.text_right_bold_border)
        worksheet.write(row,3, total_qty or 0, self.text_right_bold_border)
        worksheet.write(row,4, total_val or 0, self.text_right_bold_border)
        col=5
        for i in range(7)[::-1]:
            worksheet.write(row,col, lst[i] or 0, self.text_right_bold_border)
            col+=1
            worksheet.write(row,col, lst_val[i] or 0, self.text_right_bold_border)
            col+=1

        return worksheet, row
        
    @api.multi
    def get_aging_detail(self):
        res = {}

        start = self.date_from
        for i in range(7)[::-1]:
            if self.period_length=="Yearly":
                stop = start - relativedelta(years=1)
            elif self.period_length=="Monthy":
                stop = start - relativedelta(months=1)
            elif self.period_length=="Weekly":
                stop = start - relativedelta(weeks=1)
            else:
                stop = start - relativedelta(days=1)
            res[str(i)] = {
                'name'  : (i != 0 and (start.strftime('%d/%m/%Y') + '-' + stop.strftime('%d/%m/%Y')) or ('Up to ' + stop.strftime('%d/%m/%Y'))),
                'value':'Values',
                'stop'  : start.strftime('%Y-%m-%d'),
                'start' : (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
##            start = stop - relativedelta(days=1)
            start = stop
        return res
    
    @api.multi
    def print_excel(self):
        product_ids = self.get_products()
        
        # Define Wookbook and add sheet 
        workbook = xlwt.Workbook()
        filename = 'Stock Inventory Aging.xls'
        worksheet = workbook.add_sheet('Stock Inventory Aging')
        for i in range(0,19):
            if i == 1:
                worksheet.col(i).width = 150 * 30
            elif i > 4:
                worksheet.col(i).width = 90 * 30
            else:
                worksheet.col(i).width = 130 * 30

        # Print Excel Header
        worksheet,row = self.create_excel_header(worksheet)
        res = self.get_aging_detail()
        worksheet, row = self.create_table_header(worksheet,row+2,res)
        worksheet, row = self.create_table_values(worksheet,row,res,product_ids)
        
        
        
        
        
        #download Excel File
        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        excel_file = base64.encodestring(fp.read())
        fp.close()
        self.write({'excel_file': excel_file})

        if self.excel_file:
            active_id = self.ids[0]
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=inventory.age.wizard&download=true&field=excel_file&id=%s&filename=%s' % (
                    active_id, filename),
                'target': 'new',
            }
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
