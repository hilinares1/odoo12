import xlsxwriter
import base64
from odoo import fields, models, api
from cStringIO import StringIO
import pytz
from pytz import timezone
from datetime import datetime
import PIL
import io

class ReportStockXlsx(models.TransientModel):
    _name = "report.stock.xlsx"
    _description = "Report Stock Excel"

    @api.model
    def get_default_date_model(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))

    file_data = fields.Binary('File', readonly=True)
    type = fields.Selection([
        ('detail','Details'),
        ('history','History'),
    ], default='detail', string='Type')
    history = fields.Selection([
        ('all','ALL'),
        ('in','IN'),
        ('out','OUT'),
    ], string='History', default='all')

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['orange'],'font_color': '#000000'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': colors['yellow'],'font_color': '#000000'})
        wbf['header_yellow'].set_border()
        
        wbf['header_no'] = workbook.add_format({'bold': 1,'align': 'center','bg_color': '#FFFFDB','font_color': '#000000'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')
                
        wbf['footer'] = workbook.add_format({'align':'left'})
        
        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()
        
        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right() 
        
        wbf['title_doc'] = workbook.add_format({'bold': 1,'align': 'left'})
        wbf['title_doc'].set_font_size(12)
        
        wbf['company'] = workbook.add_format({'align': 'left'})
        wbf['company'].set_font_size(11)
        
        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right() 
        
        wbf['content_float'] = workbook.add_format({'align': 'right','num_format': '#,##0.00'})
        wbf['content_float'].set_right() 
        wbf['content_float'].set_left()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0'})
        wbf['content_number'].set_right() 
        wbf['content_number'].set_left() 
        
        wbf['content_percent'] = workbook.add_format({'align': 'right','num_format': '0.00%'})
        wbf['content_percent'].set_right() 
        wbf['content_percent'].set_left() 
                
        wbf['total_float'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()            
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()         
        
        wbf['total_number'] = workbook.add_format({'align':'right','bg_color': colors['white_orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()            
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()
        
        wbf['total'] = workbook.add_format({'bold':1, 'bg_color':colors['white_orange'], 'align':'center'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()            
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()         
        
        wbf['total_number_yellow'] = workbook.add_format({'align':'right','bg_color': colors['yellow'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()            
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()
        
        wbf['total_yellow'] = workbook.add_format({'bold':1, 'bg_color':colors['yellow'], 'align':'center'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'right', 'num_format':'#,##0.00'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()            
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()         
        
        wbf['total_number_orange'] = workbook.add_format({'align':'right','bg_color': colors['orange'],'bold':1, 'num_format': '#,##0'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()            
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()
        
        wbf['total_orange'] = workbook.add_format({'bold':1, 'bg_color':colors['orange'], 'align':'center'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()
        
        wbf['header_detail_space'] = workbook.add_format({})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()
        
        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()
        
        return wbf, workbook

    @api.multi
    def action_print(self):
        summary_id = self.env['stock.summary.new'].browse(self._context['active_id'])
        if self.type == 'detail' :
            report_name = 'Details Stock Summary %s'%summary_id.name
        else :
            if self.history == 'in' :
                history_type = 'IN'
            elif self.history == 'out' :
                history_type = 'OUT'
            else :
                history_type = 'ALL'
            report_name = 'History Stock Summary %s (%s)'%(summary_id.name,history_type)
        fp = StringIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)
        worksheet = workbook.add_worksheet(summary_id.name)

        #konten di sini
        if self.type == 'detail' :
            worksheet.set_column('A1:A1', 20)
            worksheet.set_column('B1:B1', 30)
            worksheet.set_column('C1:C1', 40)
            worksheet.set_column('D1:D1', 20)
            worksheet.set_column('E1:E1', 20)
            worksheet.set_column('F1:F1', 20)
            worksheet.set_column('G1:G1', 20)
            worksheet.set_column('H1:H1', 20)
            worksheet.set_column('I1:I1', 20)
            worksheet.set_column('J1:J1', 20)

            worksheet.write('A1', 'Code', wbf['header'])
            worksheet.write('B1', 'Product Name', wbf['header'])
            worksheet.write('C1', 'Product Category', wbf['header'])
            worksheet.write('D1', 'On hand all locations', wbf['header'])
            worksheet.write('E1', 'Start', wbf['header'])
            worksheet.write('F1', 'Qty In', wbf['header'])
            worksheet.write('G1', 'Qty Out', wbf['header'])
            worksheet.write('H1', 'Balance', wbf['header'])
            worksheet.write('I1', 'HPP', wbf['header'])
            worksheet.write('J1', 'HPJ', wbf['header'])
            row = 2
            for line in summary_id.summary_line :
                # worksheet.write('A%s' % row, line.product_id.name_get()[0][1], wbf['content'])
                worksheet.write('A%s' % row, line.product_id.default_code, wbf['content'])
                worksheet.write('B%s'%row, line.product_id.name, wbf['content'])
                worksheet.write('C%s' % row, line.product_id.categ_id.name_get()[0][1], wbf['content'])
                worksheet.write('D%s'%row, line.qty_available, wbf['content_float'])
                worksheet.write('E%s'%row, line.qty_start, wbf['content_float'])
                worksheet.write('F%s'%row, line.qty_in, wbf['content_float'])
                worksheet.write('G%s'%row, line.qty_out, wbf['content_float'])
                worksheet.write('H%s'%row, line.qty_balance, wbf['content_float'])
                worksheet.write('I%s'%row, line.hpp, wbf['content_float'])
                worksheet.write('J%s'%row, line.hpj, wbf['content_float'])
                row += 1

            worksheet.merge_range('A%s:C%s' %(row,row), 'Total', wbf['header_no'])
            worksheet.write_formula('D%s' %row, '{=subtotal(9,D2:D%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('E%s' %row, '{=subtotal(9,E2:E%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('F%s' %row, '{=subtotal(9,F2:F%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('G%s' %row, '{=subtotal(9,G2:G%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('H%s' %row, '{=subtotal(9,H2:H%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('I%s' %row, '{=subtotal(9,I2:I%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('J%s' %row, '{=subtotal(9,J2:J%s)}'%(row-1), wbf['total_float'])
        else :
            worksheet.set_column('A1:A1', 40)
            worksheet.set_column('B1:B1', 20)
            worksheet.set_column('C1:C1', 20)
            worksheet.set_column('D1:D1', 20)
            worksheet.set_column('E1:E1', 20)
            worksheet.set_column('F1:F1', 20)

            worksheet.write('A1', 'No Transaksi', wbf['header'])
            worksheet.write('B1', 'Tanggal', wbf['header'])
            worksheet.write('C1', 'Kode Barang', wbf['header'])
            worksheet.write('D1', 'Qty', wbf['header'])
            worksheet.write('E1', 'Harga', wbf['header'])
            worksheet.write('F1', 'Total', wbf['header'])
            row = 2
            domain = [('summary_id','=',summary_id.id)]
            if self.history == 'in' :
                domain.append(('type','=','in'))
            elif self.history == 'out' :
                domain.append(('type','=','out'))
            history_ids = self.env['stock.summary.line.new.history'].search(domain)
            for history in history_ids :
                worksheet.write('A%s'%row, history.name, wbf['content'])
                worksheet.write('B%s'%row, history.date, wbf['content'])
                worksheet.write('C%s'%row, history.product_code, wbf['content'])
                worksheet.write('D%s'%row, history.qty, wbf['content_float'])
                worksheet.write('E%s'%row, history.price, wbf['content_float'])
                worksheet.write('F%s'%row, history.total, wbf['content_float'])
                row += 1
            worksheet.merge_range('A%s:C%s'%(row,row), 'Total', wbf['total'])
            worksheet.write_formula('D%s' %row, '{=subtotal(9,D2:D%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('E%s' %row, '{=subtotal(9,E2:E%s)}'%(row-1), wbf['total_float'])
            worksheet.write_formula('F%s' %row, '{=subtotal(9,F2:F%s)}'%(row-1), wbf['total_float'])
        #sampai sini

        workbook.close()
        result = base64.encodestring(fp.getvalue())
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        filename = '%s %s'%(report_name,date_string)
        filename += '%2Exlsx'
        self.write({'file_data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=file_data&download=true&filename="+filename
        return {
            'name': 'Stock Summary',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
