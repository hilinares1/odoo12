import xlrd
from odoo import fields, models, api
import base64
from odoo.exceptions import Warning, ValidationError
from datetime import datetime
import sys
import logging
import operator
import psycopg2
import io

try:
    import xlwt
except ImportError:
    xlwt = None
from io import BytesIO

_logger = logging.getLogger(__name__)

PY3 = sys.version_info >= (3, 0)

if PY3:
    basestring = str
    long = int
    xrange = range
    unicode = str
    
class ImportExportForecastSaleRule(models.TransientModel):
    _name = 'import.export.forecast.sale.rule.ept'
    _description = 'Import Export Forecast Sale Rule'
        
    @api.model    
    def default_warehouse_ids(self):

        warehouses = self.env['stock.warehouse'].search([])
        return warehouses 
    
    
    @api.model
    def default_start_period_id(self):
        current_date = fields.Date.context_today(self)
        current_date_obj = datetime.strptime(str(current_date), "%Y-%m-%d")  # changes into the datetime
        start_period = self.env['requisition.period.ept'].find(dt=current_date_obj)
        return start_period
    
    @api.model
    def default_end_period_id(self):
        current_date = fields.Date.context_today(self)
        current_date_obj = datetime.strptime(str(current_date), "%Y-%m-%d")  # change for the datetime issue
        end_period = self.env['requisition.period.ept'].find(dt=current_date_obj)
        return end_period

    @api.model
    def get_period(self):
        current_date = fields.Date.context_today(self)
        periods = self.env['requisition.period.ept'].sudo().search([('date_stop', '>=', current_date)])
        return [('id', 'in', periods.ids)]

    @api.model
    def get_source_a_period(self):
        current_date = fields.Date.context_today(self)
        periods = self.env['requisition.period.ept'].sudo().search(
                [('date_start', '<=', current_date)])
        return [('id', 'in', periods.ids)]

    @api.model
    def get_source_b_period(self):
        current_date = fields.Date.context_today(self)
        periods = self.env['requisition.period.ept'].sudo().search(
                [('date_start', '<=', current_date)])
        return [('id', 'in', periods.ids)]


    choose_file = fields.Binary(string='Choose File', filters='*.xlsx', help="File extention Must be XLS, or XLSX", copy=False)
    file_name = fields.Char(string='Filename', size=512)
    requisition_log_id = fields.Many2one('requisition.log.ept', string='Log')    
    
    start_period_id = fields.Many2one("requisition.period.ept", string="Export From Period", default=default_start_period_id, help="Export Forecast Sales Rule From Given Period.")
    end_period_id = fields.Many2one("requisition.period.ept", string="To Period", default=default_end_period_id, help="Export Forecast Sales Rule to Given Period.")
    warehouse_ids = fields.Many2many("stock.warehouse", string="Warehouses", default=default_warehouse_ids, help="Export Forecast Sales Rule for given Warehouses.")
    datas = fields.Binary('File')
    type = fields.Selection(string='Choose Operations', selection=[('import', 'Import'), ('export', 'Export')],
                            default='import')
    auto_forecasted_rule = fields.Boolean(string="Auto Forecasted Rule", default=False)
    source_a_period_ids = fields.Many2many("requisition.period.ept",
                                           "requisition_period_ept_source_a",
                                           string="Compare Periods", domain=get_source_a_period)
    source_b_period_ids = fields.Many2many("requisition.period.ept",
                                           "requisition_period_ept_source_b", string="With Periods",
                                           domain=get_source_b_period)
    dest_period_ids = fields.Many2many("requisition.period.ept", string="Forecast Sales For",
                                       domain=get_period)
    forecasted_rule_datas = fields.Binary('Forecasted Rule File')
    auto_forecast_rule_as_per = fields.Selection([('actual_sales', 'Actual Sales'),
                                                  ('forecasted_sales', 'Forecasted Sales')],
                                                 string='Auto Forecast Based On', default='actual_sales')
    product_ids = fields.Many2many("product.product", string="Products")

    @api.constrains('source_a_period_ids', 'source_b_period_ids')
    def _check_same_periods(self):
        """
        Added by Udit
        This constraint will not allow to select same period to generate forecast sales rules.
        """
        if self.source_a_period_ids and self.source_b_period_ids:
            source_a = set(self.source_a_period_ids.ids)
            source_b = set(self.source_b_period_ids.ids)
            if len(source_a.intersection(source_b)) > 0:
                raise Warning("You can not compare same periods.")

    
    def download_forcasted_sales_rule_template(self):
        attachment = self.env['ir.attachment'].search([('name', '=', 'import_forcasted_sales_rule_template.xls')])
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % (attachment.id),
            'target': 'new',
            'nodestroy': False,
            }

    def create_forecasted_rule(self):
        """
        Added by Udit
        This method will create or update forecast sales rules based on actual sales or
        forecasted sales.
        """
        stock_warehouse_obj = self.env['stock.warehouse'].sudo()
        product_obj = self.env['product.product'].sudo()
        source_a_periods = self.source_a_period_ids
        source_b_periods = self.source_b_period_ids
        dest_periods = self.dest_period_ids

        if self.warehouse_ids:
            warehouses = self.warehouse_ids
        else:
            warehouses = stock_warehouse_obj.search([('company_id', 'in', self.env.user.company_ids.ids)]) or False

        if not warehouses:
            raise ValidationError("please select the Warehouse.")

        if self.product_ids:
            all_products = self.product_ids
        else:
            all_products = product_obj.with_context(active_test=True).search([('type', '=', 'product')])
        if not all_products:
            raise ValidationError("please select the Products.")

        warehouses = ",".join(map(str, warehouses.ids))
        all_products = ",".join(map(str, all_products.ids))

        if self.auto_forecast_rule_as_per == 'actual_sales':
            data = self.prepare_data_actual_sales(source_a_periods, source_b_periods, all_products, warehouses)
        else:
            data = self.prepare_data_forecasted_sales(source_a_periods, source_b_periods, all_products, warehouses)
        if not data:
            raise Warning("No Data Available For Creating Forecasted Rules.")
        try:
            created_rules = self.prepare_forecast_rules(data, dest_periods)
        except Exception as e:
            raise Warning("Rules are not created due to '%s'"%(e))
        if created_rules:
            return {'effect':{'fadeout':'slow',
                              'message':"Yeah %s, Forecasted Rules Are Created" %
                                        self.env.user.name,
                              'img_url':'/web/static/src/img/smile.svg', 'type':'rainbow_man'}}

    def prepare_forecast_rules(self, data, dest_periods):
        """
        Added by Udit
        This method will create or update forecast sales rules based on the data passed to this
        method for specified destination periods.
        :param data: Data dictionary.
        :param dest_periods: Destination periods for which the forecast sales rule will be generated.
        """
        warehouse_wise_data = {}
        for record in data:
            warehouse = record['warehouse_id']
            if warehouse in warehouse_wise_data:
                previous_data = warehouse_wise_data[warehouse]
                previous_data.append(record)
                warehouse_wise_data.update({warehouse: previous_data})
            else:
                warehouse_wise_data.update({warehouse: [record]})

        product_obj = self.env['product.product'].sudo()
        warehouse_obj = self.env['stock.warehouse'].sudo()
        forecast_sale_rule_line_obj = self.env['forecast.sale.rule.line.ept'].sudo()
        forecast_sale_rule_obj = self.env['forecast.sale.rule.ept'].sudo()
        # created_rules = self.env['forecast.sale.rule.ept'].sudo()
        count = 0
        for key, value in warehouse_wise_data.items():
            for dest_period in dest_periods:
                for dic in value:
                    count+=1
                    rule = forecast_sale_rule_obj.search([('warehouse_id', '=', dic['warehouse_id']),
                                                          ('period_id', '=', dest_period.id)],
                                                         limit=1)
                    product = product_obj.browse(dic['product_id'])
                    warehouse = warehouse_obj.browse(dic['warehouse_id'])
                    if not rule:
                        rule = forecast_sale_rule_obj.create({
                            'warehouse_id': warehouse.id,
                            'period_id': dest_period.id,
                            'global_sale_ratio': 1.0
                        })
                        # created_rules+=rule
                    rule_line = forecast_sale_rule_line_obj.search([('forecast_sale_rule_id','=', rule.id),
                                                                    ('product_id', '=',
                                                                     product.id)], limit=1)
                    if rule_line:
                        rule_line.write({'sale_ratio': dic['sales_ratio']})
                    else:
                        forecast_sale_rule_line_obj.create({
                            'forecast_sale_rule_id':rule.id,
                            'product_id':product.id,
                            'sale_ratio':dic['sales_ratio']
                        })
        return True
        # return created_rules



    def download_forecasted_rule_excel(self):
        """
        Added by Udit
        This method will generate forecast sales rules and will generate Excel file.
        :return: It will return Excel file.
        """
        stock_warehouse_obj = self.env['stock.warehouse'].sudo()
        product_obj = self.env['product.product'].sudo()
        source_a_periods = self.source_a_period_ids
        source_b_periods = self.source_b_period_ids
        dest_periods = self.dest_period_ids
        
        if self.warehouse_ids:
            warehouses = self.warehouse_ids
        else:
            warehouses = stock_warehouse_obj.search([('company_id', 'in', self.env.user.company_ids.ids)]) or False

        if not warehouses:
            raise ValidationError("please select the Warehouse.")

        if self.product_ids:
            all_products = self.product_ids
        else:
            all_products = product_obj.with_context(active_test=True).search([('type', '=', 'product')])
        if not all_products:
            raise ValidationError("please select the Products.")

        warehouses = ",".join(map(str, warehouses.ids))
        all_products = ",".join(map(str, all_products.ids))
            
        if self.auto_forecast_rule_as_per == 'actual_sales':
            data = self.prepare_data_actual_sales(source_a_periods, source_b_periods, all_products, warehouses)
        else:
            data = self.prepare_data_forecasted_sales(source_a_periods, source_b_periods, all_products, warehouses)
        if not data:
            raise Warning("No Data Available For Forecasted Rules.")
        workbook = xlwt.Workbook()
        filename, workbook = self.generate_excel_report(workbook, data, dest_periods)

        return {
            'type':'ir.actions.act_url',
            'url':'web/content/?model=import.export.forecast.sale.rule.ept&field=forecasted_rule_datas&download=true&id=%s&filename=%s' % (self.id, filename),
            'target':'new',
        }


    def generate_excel_report(self, workbook, data, dest_periods):
        """
        Added by Udit
        This method will prepare Excel file based on the data passed to it.
        :param workbook: Workbook.
        :param data: Data for which Excel file will generate.
        :param dest_periods: Destination period for which forecast will generate.
        :return: This method will return file name and workbook.
        """
        title_bold = xlwt.easyxf("font: bold on,height 230;")
        worksheet = workbook.add_sheet("Sheet{}".format(1), cell_overwrite_ok=True)
        title_count = 0
        worksheet.write(0, title_count, "warehouse", title_bold)
        title_count += 1
        worksheet.write(0, title_count, "product_sku", title_bold)
        title_count += 1
        for dest in dest_periods:
            worksheet.write(0, title_count, dest.code, title_bold)
            title_count += 1
        row=1
        product_obj = self.env['product.product'].sudo()
        warehouse_obj = self.env['stock.warehouse'].sudo()
        for record in data:
            col = 0
            product = product_obj.browse(record['product_id'])
            warehouse = warehouse_obj.browse(record['warehouse_id'])
            worksheet.write(row, col, warehouse.name)
            col+=1
            worksheet.write(row, col, product.default_code)
            col+=1
            for dest in dest_periods:
                worksheet.write(row, col, round(record['sales_ratio'],2))
                col+=1
            row+=1
        worksheet.col(0).width = 256 * 25
        worksheet.col(1).width = 256 * 20
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        self.forecasted_rule_datas = base64.encodestring(fp.read())
        fp.close()
        filename = "Forecasted_sales_rules.xls"
        return filename, workbook


    def prepare_data_actual_sales(self, source_a_periods, source_b_periods, all_products, warehouses):
        """
        Added by Udit
        This method will prepare data of actual sales for specified product and warehouse and for specified periods.
        :param source_a_periods: Compare periods.
        :param source_b_periods: Compare with periods.
        :param all_products: Comma separated product string.
        :param warehouses: Comma separated warehouse string.
        :return: This method will return list of dictionaries of forecast sales rules.
        """
        source_a_periods_str, source_b_periods_str = self.generate_query_date_string(source_a_periods, source_b_periods)
        query_data_for_source_a = self.generate_sales_of_period_actual_sales(source_a_periods_str, len(source_a_periods),
                                                                             all_products, warehouses)
        query_data_for_source_b = self.generate_sales_of_period_actual_sales(source_b_periods_str, len(source_b_periods),
                                                                             all_products, warehouses)
        new_sales_ratio_list = self.find_final_sales_ratio(query_data_for_source_a, query_data_for_source_b)
        return new_sales_ratio_list
    
    def find_final_sales_ratio(self, query_data_for_source_a, query_data_for_source_b):
        """
        Added by Udit
        This method will compare data of two list of dictionaries, finds sales ratio for same
        product and warehouse data available in both.
        :param query_data_for_source_a: List of dictionaries of compare periods.
        :param query_data_for_source_b: List of dictionaries of compare with periods.
        :return: This method will return list of dictionaries of forecast sales rules.
        """
        new_sales_ratio_list = []
        for record_source_a in query_data_for_source_a:
            # if self.auto_forecast_rule_as_per == 'actual_sales':
            data = list(filter(lambda value:value['product_id'] == record_source_a['product_id']
                                            and
                                            value['warehouse_id'] == record_source_a[
                                                'warehouse_id'], query_data_for_source_b))
            # if len(data) > 1:
            #     prepare_data_forecasted_sales
            # else:
            #     data = list(filter(lambda value:value['product_id'] == record_source_a['product_id']
            #                                     and
            #                                     value['warehouse_id'] == record_source_a['warehouse_id']
            #                        and value['period_id'] == record_source_a['period_id'], query_data_for_source_b))
            if data:
                data = data[0]
                sales_ratio = record_source_a['sales_ratio'] / data['sales_ratio'] if data['sales_ratio'] != 0 else 0
                updated_data = {'product_id':record_source_a['product_id'],
                                'warehouse_id':record_source_a['warehouse_id'],
                                # 'period_id': record_source_a['period_id'],
                                'sales_ratio':round(sales_ratio, 2)}
                new_sales_ratio_list.append(updated_data)
        return new_sales_ratio_list

    def prepare_data_forecasted_sales(self, source_a_periods, source_b_periods, all_products, warehouses):
        """
        Added by Udit
        This method will prepare data of previous forecast sales for specified product and
        warehouse and for specified periods.
        :param source_a_periods: Compare periods.
        :param source_b_periods: Compare with periods.
        :param all_products: Comma separated product string.
        :param warehouses: Comma separated warehouse string.
        :return: This method will return list of dictionaries of forecast sales rules.
        """
        periods_a_str = ",".join(map(str, source_a_periods.ids))
        periods_b_str = ",".join(map(str, source_b_periods.ids))
        query_data_for_source_a = self.generate_sales_of_period_forecasted_sales(periods_a_str, len(source_a_periods), all_products, warehouses)
        query_data_for_source_b = self.generate_sales_of_period_forecasted_sales(periods_b_str, len(source_b_periods), all_products, warehouses)
        new_sales_ratio_list = self.find_final_sales_ratio(query_data_for_source_a, query_data_for_source_b)
        return new_sales_ratio_list


    def generate_query_date_string(self, source_a_periods, source_b_periods):
        """
        Added by Udit
        This method will prepare conditional string for query period wise.
        :param source_a_periods: Compare periods.
        :param source_b_periods: Compare with periods.
        :return: This method will return conditional string for query.
        """
        source_a_periods_str = ""
        source_b_periods_str = ""
        source_a_first = True
        source_b_first = True
        for record in source_a_periods:
            date_start = record.date_start and record.date_start.strftime('%Y-%m-%d 00:00:00') or ''
            date_stop = record.date_stop and record.date_stop.strftime('%Y-%m-%d 23:59:59') or ''
            if date_start and date_stop:
                if source_a_first:
                    source_a_periods_str += "move.date between '{}' and '{}' ".format(date_start, date_stop)
                    source_a_first = False
                else:
                    source_a_periods_str += "or move.date between '{}' and '{}' ".format(date_start, date_stop)

        for record in source_b_periods:
            date_start = record.date_start and record.date_start.strftime('%Y-%m-%d 00:00:00') or ''
            date_stop = record.date_stop and record.date_stop.strftime('%Y-%m-%d 23:59:59') or ''
            if date_start and date_stop:
                if source_b_first:
                    source_b_periods_str += "move.date between '{}' and '{}' ".format(date_start, date_stop)
                    source_b_first = False
                else:
                    source_b_periods_str += "or move.date between '{}' and '{}' ".format(date_start, date_stop)
        return source_a_periods_str, source_b_periods_str

    def generate_sales_of_period_actual_sales(self, source_periods_str, duration, all_products, warehouses):
        """
        Added by Udit
        This method will prepare a query for calculating sales ratio based on past sale.
        :param source_periods_str: Period wise conditional string.
        :param duration: Length of total period.
        :param all_products: Comma separated products string.
        :param warehouses: Comma separated warehouses string.
        :return: This method will executes the sales query and returns it's result.
        """
        query = """Select 
                    * 
                    from 
                        (Select 
                            product_id, 
                            warehouse_id,
                            Round(coalesce(sum(quantity),0) / {},2) as sales_ratio
                        From 
                        (
                            select 
                                move.product_id,
                                move.location_id,
                                ware.id as warehouse_id,
                                move.product_uom_qty as quantity
                        
                            from 
                                stock_move move
                            Inner Join stock_location source on move.location_id = source.id
                            Inner Join stock_location dest on move.location_dest_id = dest.id
                            Left Join stock_warehouse ware on source.parent_path::text ~~ concat('%/', ware.view_location_id, '/%')
                            Where 
                                source.usage = 'internal' 
                                and dest.usage='customer' 
                                and move.state = 'done'
                                and move.product_id in ({})
                                and ware.id in ({}) 
                                and ({})
                        
                            Union all 
                        
                            select 
                                move.product_id,
                                move.location_id,
                                ware.id as warehouse_id,
                                move.product_uom_qty * -1 as quantity
                        
                            from 
                                stock_move move
                            Inner Join stock_location source on move.location_id = source.id
                            Inner Join stock_location dest on move.location_dest_id = dest.id
                            Left Join stock_warehouse ware on dest.parent_path::text ~~ concat('%/', ware.view_location_id, '/%')
                            Where 
                                source.usage = 'customer' 
                                and dest.usage='internal' 
                                and move.state = 'done'
                                and move.product_id in ({})
                                and ware.id in ({})
                                and ({})
                        )sd
                    Group by product_id, warehouse_id)ss where sales_ratio > 0""".format(duration,
                                                                                         all_products, warehouses, source_periods_str,
                                                                                         all_products, warehouses, source_periods_str)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return result

    def generate_sales_of_period_forecasted_sales(self, periods_str, period_count, products_str, warehouses_str):
        """
        Added by Udit
        This method will prepare a query to calculate sales ratio based on past forecast sales.
        :param periods_str: Comma separated period's string.
        :param period_count: Length of total period.
        :param products_str: Comma separated products string.
        :param warehouses_str: Comma separated warehouses string.
        :return: This method will executes the sales ratio query and returns it's result.
        """
        query = """select 
                        product_id, 
                        --period_id, 
                        warehouse_id,
                        coalesce(sum(forecast_sales),0) / {} as sales_ratio
                        --sum(forecast_sales) as sales_ratio
                    from 
                        forecast_sale_ept 
                    where 
                        period_id in ({})
                        and product_id in ({}) 
                        and warehouse_id in ({})
                    group by warehouse_id, product_id""".format(period_count, periods_str, products_str, warehouses_str)
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        return result

               
    def read_file(self, file_name, choose_file):
        """File read method.
          @param: File name and binary date
          @return: Return file radable data.
        """
        try:
            xl_workbook = xlrd.open_workbook(file_contents=base64.decodestring(choose_file))
            worksheet = xl_workbook.sheet_by_index(0)
        except Exception as e:
            error_value = str(e)
            raise ValidationError(error_value)
        return worksheet
    
    
    def get_header(self, worksheet):
        """File Header.
          @param: Xls file data
          @return: Return file Header data.
        """
        try:
            column_header = {}
            periods = {}
            normal_columns = ['product_sku', 'warehouse']
            period_obj = self.env['requisition.period.ept']
            invalid_periods = []
            for col_index in xrange(worksheet.ncols):
                value = worksheet.cell(0, col_index).value.lower()
                column_header.update({col_index: value}) 
                if value not in normal_columns:
                    period_id = period_obj.search([('code', '=ilike', value)])
                    if not period_id or len(period_id) > 1:
                        msg = "Invalid column found => " + str(value)
                        invalid_periods.append(msg)
                    else :
                        periods.update({value : col_index})
            if invalid_periods:
                if self.requisition_log_id.line_ids:
                    self.requisition_log_id.line_ids.sudo().unlink()
                error = ""
                for invalid_column in invalid_periods:
                    self.create_requisition_log_line(invalid_column, self.requisition_log_id, 'Import_forcasted_sales_rule')
                error = "Found Invalid Column Please Check the Log :- " + self.requisition_log_id.name + " "
                raise ValidationError(error)                    
                       
        except Exception as e:
            error_value = str(e)
            raise ValidationError(error_value)

        return column_header, periods
    
    
    def validate_fields(self, columnheader):
        '''
            This import pattern requires few fields default, so check it first whether it's there or not.
        '''
        require_fields = ['warehouse']
        missing = []
        for field in require_fields:
            if field not in columnheader.values():
                missing.append(field)
            
        if len(missing) > 0:
            raise ValidationError("Please provide all the required fields in file, missing fields => %s." % (missing))
        return True
    
    def fill_dictionary_from_file(self, worksheet, column_header):
        """File to dict.
          @param: Worksheet and coloumn header.
          @return:Return file dict data.
        """
        try:
            data = []
            for row_index in range(1, worksheet.nrows):
                sheet_data = {}
                for col_index in xrange(worksheet.ncols):
                    sheet_data.update({column_header.get(col_index): worksheet.cell(row_index, col_index).value})
                data.append(sheet_data)
        except Exception as e:
            error_value = str(e)
            raise ValidationError(error_value)
        return data
    
    
    def get_default_datetime(self):
        local_now = datetime.now()
        return local_now.strftime("%Y-%m-%d %H:%M:%S")
    
    
    def create_log_record(self, msg="Import Sales Forecasted Data", to_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
        log_obj = self.env['requisition.log.ept']
        log_id = log_obj.create({'log_date':to_date, 'message':msg , 'log_type':"Import_forcasted_sales_rule"})
        return log_id
    
    
    def create_requisition_log_line(self, msg, log_id, log_type='Import_forcasted_sales_rule'):
        log_line_obj = self.env['requisition.log.line.ept']
        log_line_obj.create({'log_id' : log_id.id,
                            'message':msg,
                            'log_type':log_type
                           })
    
    
    def validate_data(self, sale_data=[], periods={}):
        product_obj = self.env['product.product']   
        warehouse_obj = self.env['stock.warehouse']
        period_obj = self.env['requisition.period.ept']
        invalid_data = []
        flag = False 
        importable_data = []
        row_number = 1
        for data in sale_data:
            product_id = ''
            row_number += 1
            default_code = data.get('product_sku', '')
            if type(data.get('product_sku')) == type(0.0):
                default_code = str(int(data.get('product_sku')))
            if default_code:
                product_id = product_obj.search([('default_code', '=', default_code)])
                if not product_id:
                    msg = 'Product not found Of Related SKU !! " %s ". Row Number : %s ' % (default_code, row_number)
                    invalid_data.append(msg)
                    flag = True
                if not product_id.can_be_used_for_coverage_report_ept:
                    msg = 'Product is not going to be use for Coverage Report !! %s. Row Number : %s ' % (default_code, row_number)
                    invalid_data.append(msg)
                    flag = True
                    
            warehouse = str(data.get('warehouse', ''))
            if not warehouse:
                msg = 'Invalid Warehouse!! => %s Row Number : %s ' % (data, row_number)
                invalid_data.append(msg)
                flag = True
                
            warehouse = warehouse.strip()
            warehouse_id = warehouse_obj.search([('name', '=', warehouse)])
            if not warehouse_id:
                msg = 'Warehouse not found!! " %s " Row Number : %s ' % (warehouse, row_number)
                invalid_data.append(msg)
                flag = True
            
            for key in periods.keys():
                period_id = period_obj.search([('code', 'ilike', key)])
                if not data.get(key) :
                    continue
                if isinstance(data.get(key, 0.0), (float)) :
                    vals = {
                          'warehouse_id' : warehouse_id.id,
                          'period_id' : period_id.id,
                          'global_sale_ratio':data.get(key, 1.0),
                          'product_id' : product_id and product_id.id or '',
                          'sale_ratio' : data.get(key, 1.0),
                          }
                    importable_data.append(vals)                    
                else :
                    msg = 'Invalid Data " %s " Of Period %s Row Number : %s ' % (data.get(key, 0.0), period_id.code, row_number)
                    invalid_data.append(msg)
                    flag = True
            if flag:
                continue
    
        if len(invalid_data) > 0:
            error = ""
            for err in invalid_data:
                self.create_requisition_log_line(err, self.requisition_log_id, 'Import_forcasted_sales_rule')
                error = error + err + "\n"
            raise ValidationError("Please Correct Data First and then Import File.For More Detail See the Log  %s." % (self.requisition_log_id.name))

        return importable_data
    
    def validate_process(self):
        '''
            Validate process by checking all the conditions and return back with sale order object
        '''   
        if not self.choose_file:
            raise ValidationError('Please select file to process...')
    
    
    def do_import(self):
        if self.file_name and self.file_name[-3:] != 'xls' and self.file_name[-4:] != 'xlsx':
            raise Warning("Please Provide Only .xls OR .xlsx File to Import Forecast Sales!!!")
        to_date = self.get_default_datetime()
        self.requisition_log_id = self.create_log_record(to_date=to_date)
        try:
            forecast_sale_rule_obj = self.env['forecast.sale.rule.ept']
            forecast_sale_rule_line_obj = self.env['forecast.sale.rule.line.ept']
            worksheet = self.read_file(self.file_name, self.choose_file)
            column_header, periods = self.get_header(worksheet)
            
            if self.validate_fields(column_header):
                sale_data = self.fill_dictionary_from_file(worksheet, column_header)
                importable_data = self.validate_data(sale_data, periods)
                
                for data in importable_data:
                    product_id = data.get('product_id', False)
                    warehouse_id = data.get('warehouse_id', False)
                    period_id = data.get('period_id', False)
                    global_sale_ratio = data.get('global_sale_ratio', 1.0)
                    sale_ratio = data.get('sale_ratio', 1.0)
                    
                    rule = forecast_sale_rule_obj.search([('warehouse_id', '=', warehouse_id), ('period_id', '=', period_id)])
                    if not rule:
                        if product_id:
                            rule = forecast_sale_rule_obj.create({
                                    'warehouse_id' : warehouse_id,
                                    'period_id' : period_id,
                                    'global_sale_ratio':1.0
                                    })
                            rule_line = forecast_sale_rule_line_obj.search([('forecast_sale_rule_id', '=', rule.id), ('product_id', '=', product_id)])
                            if rule_line:
                                rule_line.write({
                                    'sale_ratio':sale_ratio
                                    })
                            else:
                                rule_line = forecast_sale_rule_line_obj.create({
                                    'forecast_sale_rule_id':rule.id,
                                    'product_id':product_id,
                                    'sale_ratio':sale_ratio
                                    })
                        else:
                            rule = forecast_sale_rule_obj.create({
                                    'warehouse_id' : warehouse_id,
                                    'period_id' : period_id,
                                    'global_sale_ratio':global_sale_ratio
                                    })            
                    else:
                        if product_id:
                            rule_line = forecast_sale_rule_line_obj.search([('forecast_sale_rule_id', '=', rule.id), ('product_id', '=', product_id)])
                            if rule_line:
                                rule_line.write({
                                    'sale_ratio':sale_ratio
                                    })
                            else:
                                rule_line = forecast_sale_rule_line_obj.create({
                                    'forecast_sale_rule_id':rule.id,
                                    'product_id':product_id,
                                    'sale_ratio':sale_ratio
                                    })
                        else:
                            rule.write({
                               'global_sale_ratio':global_sale_ratio
                              })
        
        except Exception as e:
            self.validate_process()
            self.requisition_log_id.write({'message' : 'Process Failed, please refer log lines for more details.', 'state':'fail'})
            self._cr.commit()
            raise Warning(str(e))

        if not self.requisition_log_id.line_ids:
            self.requisition_log_id.write({'message' : 'Sales forecast Rule data imported successfully...', 'state':'success'})
            return {'effect': {'fadeout': 'slow', 'message': "Yeah! Forecast Sale Rule Imported successfully.",
                           'img_url': '/web/static/src/img/smile.svg', 'type': 'rainbow_man', }}
        else:
            self.requisition_log_id.write({'message' : 'Process Failed, please refer log lines for more details.', 'state':'fail'})
        return True
    ####################### EXPORT ####################################
 
    
    def export_forecast_sales_rule(self):
        if self.start_period_id.date_start >= self.end_period_id.date_stop:
            raise Warning("End Date is Must be Greater then Start Date ! ")
        fsr_dict = {}

        try:
            self._cr.execute("CREATE EXTENSION IF NOT EXISTS tablefunc;")
            from_date = self.start_period_id.date_start
            to_date = self.end_period_id.date_stop
            warehouse_ids = []
            for warehouse in self.warehouse_ids:
                warehouse_ids.append(warehouse.id)
            warehouse_ids = '(' + str(warehouse_ids or [0]).strip('[]') + ')'        
            file_header1 = {'warehouse': 0, 'product_sku' : 1}
            column_no = 2
            column_list = ""
            select_column_list = ""
            file_header2 = {} 
            file_header = {}
            periods = self.start_period_id.search([('date_start', '>=', from_date), ('date_stop', '<=', to_date)])
            if periods:
                for period in periods:
                    column_list = column_list + ", %s float" % (period.code)  # #  ,Jan2017 float, Jan2017 float
                    select_column_list = select_column_list + ",coalesce(%s,0) as %s" % (period.code, period.code.lower())  # ,coalesce(Jan2017,0) as jan2017
                    file_header2.update({period.code.lower(): column_no})
                    column_no += 1
            file_header.update(file_header1) 
            file_header.update(file_header2)        
            query_line = """select 
                                warehouse,
                                product_sku
                                %s
                            from crosstab(
                                            'Select 
                                                w.name || COALESCE(p.default_code,'''') AS row_name,
                                                w.name as warehouse,
                                                p.default_code as product_sku,
                                                per.code as period,
                                                sale_ratio
                                            from     
                                                 (
                                                    Select *
                                                        From
                                                            (
                                                            select warehouse_id,null as product_id,f.period_id,f.global_sale_ratio as sale_ratio
                                                                from
                                                                    forecast_sale_rule_ept f
                                                                    join requisition_period_ept per on per.id = f.period_id
                                                                    where per.date_start >= ''%s'' and per.date_stop <= ''%s'' and f.warehouse_id in %s
                                                            Union All
                                                            select warehouse_id,product_id,f.period_id,l.sale_ratio
                                                                from 
                                                                    forecast_sale_rule_ept f
                                                                    join forecast_sale_rule_line_ept l on l.forecast_sale_rule_id = f.id
                                                                    join product_product p on p.id = l.product_id
                                                                    Join requisition_period_ept per on per.id = f.period_id
                                                                    where per.date_start >= ''%s'' and per.date_stop <= ''%s'' and f.warehouse_id in %s
                                                            )T
                                                )Sales 
                                                Inner Join stock_warehouse w on w.id = sales.warehouse_id
                                                Inner Join requisition_period_ept per on per.id = sales.period_id
                                                left join product_product p on p.id = sales.product_id
                                                order by 1,2;',
                                            'Select code from requisition_period_ept where date_start >= ''%s'' and date_stop <= ''%s'' order by date_start') 
                            as newtable (row_name text, warehouse varchar,product_sku varchar %s)""" % (select_column_list, from_date, to_date, warehouse_ids, from_date, to_date, warehouse_ids, from_date, to_date, column_list)
            
            self._cr.execute(query_line)
            fsr_dict = self._cr.dictfetchall() 
        except psycopg2.DatabaseError as e:
            if e.pgcode == '58P01':
                raise Warning("To enable Export Forecast Sale Rule, Please install Postgresql - Contrib in Postgresql")     
        
        if fsr_dict:
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet("Forecast Sale Rule Report", cell_overwrite_ok=True)
            # ## it will return sorted data in list of tuple (sorting based on value)
            sorted_file_header = sorted(file_header.items(), key=operator.itemgetter(1))
            header_bold = xlwt.easyxf("font: bold on, height 250; pattern: pattern solid, fore_colour gray25;alignment: horizontal center")
            column = 0
            for header in sorted_file_header:
                worksheet.write(0, header[1], header[0], header_bold)
                column += 1
            row = 1
            for sale in fsr_dict:
                for header in sorted_file_header:
                    col_no = header[1]
                    value = sale.get(header[0], '')
                    if value:
                        worksheet.write(row, col_no, value)
                row += 1   
            
            fp = BytesIO()
            workbook.save(fp)
            fp.seek(0)
            report_data_file = base64.encodestring(fp.read())
            fp.close()
            self.write({'datas':report_data_file})
           
            return {
            'type' : 'ir.actions.act_url',
            'url':   'web/content/?model=import.export.forecast.sale.rule.ept&field=datas&download=true&id=%s&filename=Forecast_sale_rule_report.xls' % (self.id),
            'target': 'new',
            }    
