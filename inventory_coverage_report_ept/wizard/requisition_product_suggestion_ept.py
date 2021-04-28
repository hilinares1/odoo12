from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import math
import xlsxwriter
import base64
from io import BytesIO
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo.addons.inventory_coverage_report_ept.sortedcontainers.sorteddict import SortedDict

report_frame = {}
use_forecasted_sales_for_requisition = 0
class RequisitionProductSuggestion(models.TransientModel):
    _name = 'requisition.product.suggestion.ept'
    _description = "Inventory Coverage Report / Product Recommandation"

    @api.model
    def _get_default_backup_stock_days(self):
        backup_days = self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.is_default_requisition_backup_stock_days')
        return backup_days and backup_days or 60

    @api.model
    def get_default_past_sale_start_from(self):
        start_date = fields.Date.context_today(self)
        start_date_obj = datetime.strptime(str(start_date), "%Y-%m-%d")
        start_date_obj = start_date_obj.strftime("%Y-%m-%d")
        return start_date_obj

    def default_is_use_forecast_sale_for_requisition(self):
        return eval(self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.use_forecasted_sales_for_requisition'))

    def default_warehouse_ids(self):
        warehouses = self.env['stock.warehouse'].search([])
        return warehouses

    @api.model
    def default_company(self):
        allow_company = self._context.get('allowed_company_ids')
        return allow_company

    def default_type(self):
        type = 'actual_past_sales'
        if eval(self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.use_forecasted_sales_for_requisition')):
            type = 'forecast_sales'
        return type

    name = fields.Char(string="Name", default="Product Suggestion")
    inventory_analysis_of_x_days = fields.Integer(string="Inventory Analysis of X Days", default=_get_default_backup_stock_days)
    warehouse_ids = fields.Many2many('stock.warehouse', string="Warehouses", default=default_warehouse_ids)
    product_suggestion_line_ids = fields.One2many('requisition.product.suggestion.line.ept', 'product_suggestion_id', string='Product Suggestion Lines')
    is_use_forecast_sale_for_requisition = fields.Boolean("Use Forecast sale For Requisition", default=default_is_use_forecast_sale_for_requisition, copy=False)
    requisition_past_sale_start_from = fields.Date(string='Past Sales Start From', default=get_default_past_sale_start_from)
    product_ids = fields.Many2many('product.product', string="Products to Analyse")
    supplier_suggestion_type = fields.Selection([('quick', 'Quickest'),
                                                 ('cheap', 'Cheapest')], string="Choose Vendor", default='cheap')
    product_inventory_coverage_detail_file = fields.Binary("File")
    has_pending_moves = fields.Boolean('Has Pending Moves?', default=False, help="Has Pending Moves to be rescheduled?")
    inventory_coverage = fields.Boolean("Is Inventory Coverage Report?", default=False)
    select_products = fields.Boolean("Choose Products", default=False, help="If want to Get details for only selected products then select products and it will check for selected products only otherwise for all")
    select_warehouses = fields.Boolean("Choose Warehouses", default=False, help="If want to Get details for only selected Warehouses then select Warehouses and it will check for selected Warehouses only otherwise for all")
    show_detailed_report = fields.Boolean("Show Detailed Report", default=True)
    show_products = fields.Selection([('all', 'All'), ('out_of_stock_product', 'Out of Stock Product Only'), ('in_stock_product', 'In Stock Product Only')],
                                     string="Product Visibility", default="all",
                                     help="All : Give Report with all details whether it is in stock or out of stock."
                                            "Out of Stock Product Only : Give Report with Only Out Of Stock Products"
                                            " In Stock Product Only : Give Report with Only In Stock Products"
                                    )
    include_draft_quotations = fields.Boolean("Include Draft Quotations (Purchase RFQ)")
    check_stock_in_other_warehouses = fields.Boolean("Check Stock in Other Warehouses", default=False, help="If Report is for Out of Stock Products, Check stock Availability in Other Warehouses from chosen Warehouses")
    company_ids = fields.Many2many('res.company', string='Company', default=default_company)

    @api.onchange('show_products')
    def onchange_show_products(self):
        for record in self:
            if record.show_products == 'in_stock_product':
                record.check_stock_in_other_warehouses = False

    def check_forecast_sales_data(self, products, warehouses, start_date, end_date):
        """
        If using forecasting method for coverage and not available forecast record
        for this period or product than got the warning.
        """
        product_ids = products and products.ids or []
        product_ids_str = '(' + str(product_ids or [0]).strip('[]') + ')'
        requisition_period_ids = self.env['requisition.period.ept'].search([('date_start', '<=', end_date), ('date_stop', '>=', start_date)])
        list_period_ids = [period.id for period in requisition_period_ids]
        period_ids_str = '(' + str(list_period_ids or [0]).strip('[]') + ')'
        warehouse_ids_str = '(' + str(warehouses and warehouses.ids or [0]).strip('[]') + ')'
        not_found_query = """
                Select 
                    product.id as product_id, 
                    warehouse.id as warehouse_id,
                    period.id as period_id
                From 
                    product_product product, stock_warehouse warehouse, requisition_period_ept period
                Where 
                    product.id in {product_ids} And 
                    warehouse.id in {warehouse_ids} And 
                    period.id in {period_ids}
                
                Except
                
                Select 
                    product_id, 
                    warehouse_id, 
                    period_id
                from forecast_sale_ept
                Where 
                    product_id in {product_ids} And 
                    warehouse_id in {warehouse_ids} And 
                    period_id in {period_ids}
            """
        not_found_query = not_found_query.format(product_ids=product_ids_str, warehouse_ids=warehouse_ids_str, period_ids=period_ids_str)
        self._cr.execute(not_found_query)
        res_dict = self._cr.dictfetchall()
        return res_dict

###### Added by Viraj #######

    def get_next_date(self, date, days=1):
        d1_obj = date
        d2_obj = d1_obj + timedelta(days=days)
        return d2_obj

    def get_periods_of_date(self, start_date, end_date):
        d1_obj = start_date # i.e, datetime.datetime(2019, 12, 21, 0, 0)  # change for datetime issue
        d2_obj = end_date  #i.e, datetime.datetime(2020, 2, 18, 0, 0) # change for datetime issue
        res = {}
        date_dict = {}
        frame_number = 1
        dt = d1_obj # datetime obj of start date i.e., datetime.datetime(2019, 12, 21, 0, 0)
        while dt <= d2_obj:
            period = self.env['requisition.period.ept'].find(dt=dt) # perid id obj i.e, requisition.period.ept(9,)
            temp_obj = period.date_stop # datetime obj of end of period date i.e, datetime.datetime(2019, 12, 31, 0, 0)
            if temp_obj > d2_obj:
                temp_obj = d2_obj
            res.update({(dt, temp_obj): frame_number})
            # date_dict.update({frame_number: (dt, temp_obj)})  # update dict i.e, OrderedDict([(1, {9: ('2019-12-21', '2019-12-31')})])
            frame_number = frame_number + 1 #increase frame number
            dt = temp_obj + timedelta(days=1) # update dt for next month i.e.,datetime.datetime(2020, 1, 1, 0, 0)
        return SortedDict(res) # i.e., (OrderedDict([(1, {9: ('2019-12-21', '2019-12-31')}), (2, {10: ('2020-01-01', '2020-01-31')}), (3, {11: ('2020-02-01', '2020-02-18')})]),
                              # OrderedDict([(1, {9: 10}), (2, {10: 30}), (3, {11: 17})]))

    def prepare_frame_period_wise(self, report_start_date, report_end_date):
        frame_period_wise = self.get_periods_of_date(report_start_date, report_end_date)
        return frame_period_wise

    def prepare_main_frame(self, report_start_date, report_end_date, products, warehouses, analysis_days, forecast_stock_dict=False):
        """
                Split frames period wise, incoming and out_of stock product wise
                param: product: product_id
                       warehouse: warehouse_id
                       start_date: start_date of analysis of forecast
                       end_date: End date of analysis of forecast
                       ads: ads of month

                return: period_dict : Period wise framing ,
                        days_dict: Days count of framing,
                        incoming: Incoming quantity,
                        opening: Current stock of frame,
                        closing: Closing stock of frame,
                        total_coverage_days: Coverage days count frame wise,
                        stock_state: Stock state like 'in_stock', 'out_stock' frame wise
        """
        frame_period_wise = self.prepare_frame_period_wise(report_start_date, report_end_date)
        warehouse_ids = warehouses and '(' + str(warehouses).strip('[]') + ')' or False
        product_ids = products and '(' + str(products).strip('[]') + ')' or False
        is_warehouse_selected = True if len(warehouses) > 0 else False
        is_product_selected = True if len(products) > 0 else False

        ads = self.get_product_ads(product_ids, warehouse_ids, is_product_selected, is_warehouse_selected)
        incomings = self.get_product_incoming(product_ids, warehouse_ids, analysis_days, is_product_selected, is_warehouse_selected)
        products_stock = self.get_product_stock(product_ids, warehouse_ids, is_product_selected, is_warehouse_selected, forecast_stock_dict=forecast_stock_dict)

        #convert list of dict to dict of dict for seraching purpose in framing
        # Existing : [{'product_id':1234, warehouse_id: 1, net_on_hand:25}, {}]
        # Coverted Dict : {1234 : {1 : 25}}
        stock_dict = {(stock_data.get('product_id'), stock_data.get('warehouse_id')): stock_data.get('net_on_hand') for stock_data in products_stock}
        incoming_qty_dict = {}
        for incoming_dict in incomings:
            if incoming_qty_dict.get((incoming_dict.get('product_id', False), incoming_dict.get('warehouse_id', False)), False):
                incoming_qty_dict.get((incoming_dict.get('product_id'), incoming_dict.get('warehouse_id'))).update({incoming_dict.get('incoming_date'): incoming_dict.get('incoming')})
            else:
                incoming_qty_dict.update({(incoming_dict.get('product_id'), incoming_dict.get('warehouse_id')): {incoming_dict.get('incoming_date'): incoming_dict.get('incoming')}})

        if self.get_use_forecasted_sales_for_requisition() == 1:
            ads_qty_dict = {
                (ads_dict.get('product_id'), ads_dict.get('warehouse_id'),ads_dict.get('period_id')): ads_dict.get('ads', 0.0) for ads_dict in ads}
        else:
            ads_qty_dict = {(ads_dict.get('product_id'), ads_dict.get('warehouse_id')):  ads_dict.get('ads', 0.0) for ads_dict in ads}

        self.prepare_main_frame_data(stock_dict, incoming_qty_dict, ads_qty_dict, products, warehouses, SortedDict(frame_period_wise), ads)
        return report_frame

    def prepare_main_frame_data(self, stock_dict, incoming_qty_dict, ads_qty_dict, products, warehouses,frame_period_wise, ads):
        """
        Prepare main temporary frame
        month wise.
        :param stock_dict:
        :param incoming_qty_dict:
        :param ads_qty_dict:
        :param products:
        :param warehouses:
        :param frame_period_wise:
        :return:
        """
        main_frame = {}
        period_obj = self.env['requisition.period.ept']
        for product_id in products:
            for warehouse_id in warehouses:
                frame = {}
                if round(stock_dict.get((product_id, warehouse_id), 0.0), 2) == 0.0 and not incoming_qty_dict.get((product_id, warehouse_id), False):
                    if self.get_use_forecasted_sales_for_requisition() == 1:
                        ads_sum = sum([ads_dict.get('ads', 0.0) for ads_dict in ads if ads_dict.get('product_id') == product_id and ads_dict.get('warehouse_id') == warehouse_id])
                        if ads_sum == 0.0:
                            continue
                    elif self.get_use_forecasted_sales_for_requisition() == 0 and round(ads_qty_dict.get((product_id, warehouse_id), 0.0), 2) == 0.0:
                        continue

                for period_id, frame_number in frame_period_wise.items():
                    # incoming between start date and end date of frame
                    incoming_dict = {sch_date: qty
                                     for sch_date, qty in SortedDict(incoming_qty_dict.get((product_id, warehouse_id), {})).items()
                                     if period_id[0] <= sch_date <= period_id[1]}

                    # Find period of frame date
                    period = period_obj.find(dt=period_id[0])

                    # Create main frame with data
                    frame.update({frame_number: {'start_date': period_id[0],
                                                 'end_date': period_id[1],
                                                 'opening_stock': stock_dict.get(
                                                     (product_id, warehouse_id),
                                                     False) and stock_dict.get(
                                                     (product_id, warehouse_id), 0.0) or 0.0,
                                                 'ads': round(ads_qty_dict.get((product_id, warehouse_id),0.0), 2)
                                                 if ads_qty_dict.get((product_id, warehouse_id),False)
                                                 else round(ads_qty_dict.get((product_id, warehouse_id, period.id), 0.0), 2)
                                                 if ads_qty_dict.get((product_id, warehouse_id, period.id), False)
                                                 else 0.0,
                                                 'is_incoming': True if incoming_dict else False,
                                                 'incomings': incoming_dict or {},
                                                 'closing_stock': 0.0
                                                 }})

                # Append all frame of product and warehouse in main frame
                main_frame.update({(product_id, warehouse_id): SortedDict(frame)})

                #Create final frame from main frame like 1.1,1.2,2.1,2.2
                self.create_final_report_frame(main_frame, product_id, warehouse_id)
        return report_frame

    def calculate_coverage_days(self, start_date, end_date, ads, opening_stock=0, incoming=0):
        out_of_stock_days = in_stock_days = closing_stock = 0
        stock = opening_stock + incoming
        diff_days = (end_date - start_date).days + 1
        coverage = round(stock / (ads if ads > 0 else 0.001), 0)
        in_stock_days = diff_days
        if coverage <= diff_days:
            in_stock_days = coverage
            out_of_stock_days = diff_days - coverage
            closing_stock = stock - round(coverage * ads,0) if coverage != 0.0 else 0.0
        else:
            closing_stock = stock - round(diff_days * ads,0)

        return out_of_stock_days, in_stock_days, round(closing_stock, 0) if round(closing_stock, 0) >=0 else 0

    def update_data_in_new_frame(self, product_id, warehouse_id, ads, opening_stock, closing_stock, start_date, end_date, frame_number, state, incoming):
        """
        update and create framing data
        If call from recommandation report than cehck the ratio of out stock.
        :param product_id:
        :param warehouse_id:
        :param ads:
        :param opening_stock:
        :param closing_stock:
        :param start_date:
        :param end_date:
        :param frame_number:
        :param state:
        :param incoming:
        :return:
        """
        days = (end_date - start_date).days + 1
        forecasted_sales = ads * days
        closing_stock = (opening_stock + incoming) - round(forecasted_sales,0)
        if closing_stock <= 0:
            closing_stock = 0

        if report_frame.get((product_id, warehouse_id), False):
            report_frame.get((product_id, warehouse_id)).update({frame_number:
                        {
                            'start_date': start_date,
                            'end_date': end_date,
                            'ads': ads or 0.0,
                            'incoming':incoming,
                            'is_incoming': True if incoming > 0 else False,
                            'opening_stock': opening_stock or 0.0,
                            'closing_stock': closing_stock or 0.0,
                            'state': state,
                            'days': days,
                            'forecasted_sales': round(forecasted_sales, 0) or 0.0,
                        }
                    })
        else:
            report_frame.update({
                (product_id, warehouse_id):
                    {frame_number:
                        {
                            'start_date': start_date,
                            'end_date': end_date,
                            'ads': ads or 0.0,
                            'incoming': incoming,
                            'is_incoming': True if incoming > 0 else False,
                            'opening_stock': opening_stock or 0.0,
                            'closing_stock': closing_stock or 0.0,
                            'state': state,
                            'days': days,
                            'forecasted_sales':round(forecasted_sales,0) or 0.0,
                        }
                    }
            })

        if not self.inventory_coverage:
            sellers = self.env['product.supplierinfo']
            product = self.env['product.product'].browse(product_id)
            if self.supplier_suggestion_type == 'quick':
                sellers = product.seller_ids.sorted('delay')
            elif self.supplier_suggestion_type == 'cheap':
                sellers = product.seller_ids.sorted('price')
            else:
                sellers = product.seller_ids.filtered(lambda s: s.sequence == 1)
            report_frame.get((product_id, warehouse_id)).get(frame_number).update({'sellers': sellers and sellers[0].name.id or False})

            use_out_stock_percent = eval(self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.use_out_stock_percent'))
            if use_out_stock_percent:
                out_stock_percent = float(self.env['ir.config_parameter'].sudo().get_param(
                    'inventory_coverage_report_ept.out_stock_percent'))
                report_frame.get((product_id, warehouse_id)).get(frame_number).update(
                    {'out_of_stock_percent': True if state == 'out_stock' and (days * 100 / self.inventory_analysis_of_x_days) >= out_stock_percent else False})
            else:
                report_frame.get((product_id, warehouse_id)).get(frame_number).update({'out_of_stock_percent': True if state == 'out_stock' else False})

        SortedDict(report_frame.get((product_id, warehouse_id)))
        return True

    def create_new_frame(self, product_id, warehouse_id, ads, opening_stock, incoming, start_date, sub_frame_end_date, frame_number):
        """
        Create new frame for split the frame
        :param product_id: product.id
        :param warehouse_id: warehouse.id
        :param ads: ads
        :param opening_stock: opening stock
        :param incoming: incoming qty
        :param start_date: start date
        :param sub_frame_end_date: end date
        :param frame_number: frame number which need to split
        :return: new frame_number and it's end date
        """
        out_of_stock_days, in_stock_days, closing_stock = self.calculate_coverage_days(start_date, sub_frame_end_date, ads, opening_stock, incoming)
        calculated_opening = opening_stock
        if out_of_stock_days > 0:
            if in_stock_days > 0:
                frame_number = frame_number + 0.1
                new_date = self.get_next_date(start_date, in_stock_days - 1)
                self.update_data_in_new_frame(
                    product_id, warehouse_id, ads, calculated_opening, closing_stock, start_date, new_date, frame_number, 'in_stock', incoming
                )
                calculated_opening = closing_stock
                closing_stock = 0
                incoming = 0
            frame_number = frame_number + 0.1
            new_date = start_date if in_stock_days <= 0 else self.get_next_date(start_date, in_stock_days)
            self.update_data_in_new_frame(
                product_id, warehouse_id, ads, calculated_opening, closing_stock, new_date, sub_frame_end_date, frame_number, 'out_stock', incoming
            )
        elif in_stock_days > 0:
            frame_number = frame_number + 0.1
            self.update_data_in_new_frame(
                product_id, warehouse_id, ads, calculated_opening, closing_stock, start_date, sub_frame_end_date, frame_number, 'in_stock', incoming
            )
        return frame_number, sub_frame_end_date

    def extract_frame_data(self, data_dict):
        """
        get the data from the data dict and fetch data from dict
        :param data_dict: {'is_incoming': True/False,
         'start_date': YYYY-MM-DD with date object,
         'end_date':YYYY-MM-DD with date object,
         'ads': 2,
         'opening_stock': 49,
         'closing_stock: 35'}
        :return:
        """
        is_incoming = data_dict.get('is_incoming', False)
        start_date = data_dict.get('start_date', False)
        end_date = data_dict.get('end_date', False)
        ads = data_dict.get('ads', False)
        opening_stock = data_dict.get('opening_stock', False)
        closing_stock = data_dict.get('closing_stock', False)
        return start_date, end_date, ads, opening_stock, closing_stock, is_incoming

    def get_opening_stock_from_frame(self, product_id, warehouse_id, frame_number):
        """
        Get the closing stock from framing for the set as opening stock in new frame
        :param product_id: product.id
        :param warehouse_id: warehouse.id
        :param frame_number: frame number
        :return: closing stock of which give frame number
        """
        return report_frame.get((product_id, warehouse_id), {}).get(frame_number, {}).get('closing_stock',0) or 0

    def update_frame_opening(self, frame_number, dict):
        closing_stock = dict.get(frame_number - 1).get('closing_stock')
        dict.get(frame_number).update({'opening_stock': closing_stock})
        return True

    def create_final_report_frame(self, main_frame, product_id, warehouse_id):
        """
        Create framing with 1.1,1.2,2.1,3.1
        check if incoming than split and during frame stock going to out of stock than split
        :param main_frame: {('product_id', 'warehouse_id'):{1:{'start_date': 2019-12-01(In date object format),
         'end_date': 2019-12-12 (in date object format)
        'opening_stock':15,
         'ads': 161.22,
        'incoming':{'schedule_date':'qty'},
         'is_incoming': 'True or False',
          'state': 'in_stock or out_of_stock',
          'days':10,
          'forecasted_sales':12}}}
        :param product_id: product.id
        :param warehouse_id: warehouse.id
        :return:
        """
        monthly_frame = main_frame.get((product_id, warehouse_id), {})
        for frame_number, data in monthly_frame.items():
            if frame_number > 1:
                self.update_frame_opening(frame_number, monthly_frame)
            start_date, end_date, ads, opening_stock, closing_stock, is_incoming = self.extract_frame_data(data)
            next_frame_start_date = start_date
            last_pick_incoming = 0
            report_frame_number = frame_number
            frame_stock = opening_stock
            incoming = 0
            total_incomings = len(data.get('incomings'))
            if is_incoming:
                for schedule_date, qty in SortedDict(data.get('incomings')).items():
                    add_days = 0 if schedule_date == start_date else -1
                    sub_frame_end_date = self.get_next_date(schedule_date, days= add_days)

                    if report_frame_number != frame_number:
                        frame_stock = self.get_opening_stock_from_frame(product_id, warehouse_id, report_frame_number)

                    ### IF Incoming is there on the first day of the frame then we have to create frame with single day
                    if schedule_date == start_date:
                        report_frame_number, sub_frame_end_date = self.create_new_frame(product_id,
                                                                                        warehouse_id,
                                                                                        ads,
                                                                                        frame_stock,
                                                                                        qty,
                                                                                        schedule_date,
                                                                                        schedule_date,
                                                                                        report_frame_number)
                    else:
                        report_frame_number, sub_frame_end_date = self.create_new_frame(product_id,
                                                                                        warehouse_id,
                                                                                        ads,
                                                                                        frame_stock,
                                                                                        last_pick_incoming,
                                                                                        next_frame_start_date,
                                                                                        sub_frame_end_date,
                                                                                        report_frame_number)

                    next_frame_start_date = self.get_next_date(sub_frame_end_date, days=1)
                    if schedule_date == start_date:
                        last_pick_incoming = 0
                    else:
                        last_pick_incoming = qty
                # Last frame
                frame_stock = self.get_opening_stock_from_frame(product_id, warehouse_id, report_frame_number)
                report_frame_number, sub_frame_end_date = self.create_new_frame(product_id, warehouse_id, ads, frame_stock, last_pick_incoming, next_frame_start_date, end_date, report_frame_number)
            else:
                report_frame_number, sub_frame_end_date = self.create_new_frame(product_id, warehouse_id, ads, frame_stock, 0, start_date, end_date, report_frame_number)
            frame_stock = self.get_opening_stock_from_frame(product_id, warehouse_id, report_frame_number)
            data.update({'closing_stock' : frame_stock})
        return True

    def get_product_stock(self, product_ids, warehouse_ids, is_product_selected=False, is_warehouse_selected=False, forecast_stock_dict=False):
        """
        Get product stock
        :param product_ids: All product_ids in tuple
        :param warehouse_ids: All warehouses in tuple
        :param is_product_selected: Check is products selected
        :param is_warehouse_selected: Check is warehouse selected
        :return: data of stock i.e,[{'product_id':650008, 'warehouse_id': 1, 'net_on_hand': 12.0}]
        """
        if forecast_stock_dict:
            stock = [{'product_id': key[0], 'warehouse_id':key[1],'net_on_hand': value} for key, value in forecast_stock_dict.items()]
        else:
            self._cr.execute("""
                                SELECT
                                product_id,
                                warehouse_id,
                                net_on_hand
                                FROM
                                get_product_stock
                                where
                                 1 = case when %s = False then 1 else 
                                            case when warehouse_id in %s then 1 else 0 end 
                                     end
                                And  
                                1 = case when %s = False then 1 else 
                                        case when product_id in %s then 1 else 0 end 
                                    end
                                        """ % (is_warehouse_selected, warehouse_ids, is_product_selected, product_ids))
            stock = self._cr.dictfetchall()
        return stock

    def get_product_incoming(self, products, warehouses, analysis_days, is_product_selected=False, is_warehouse_selected=False):
        """
        Get the product incomings
        :param products: all selected products
        :param warehouses: all selected warehouses
        :param is_product_selected: Check is products selected
        :param is_warehouse_selected: Check is warehouse selected
        :return: data of incoming in list of dict format i.e,[{'incoming_date':'2019-012-15', 'product_id':650008, 'warehouse_id': 1, 'incoming':10.0}]
        """
        self._cr.execute("""
                        SELECT
                        incoming_date,
                        product_id as product_id,
                        warehouse_id as warehouse_id,
                        incoming
                        FROM
                        get_incoming_data
                        WHERE
                            1 = case when %s = False then 1 else 
                                    case when warehouse_id in %s then 1 else 0 end 
                                end
                            And  
                            1 = case when %s = False then 1 else 
                                    case when product_id in %s then 1 else 0 end 
                                end
                        AND
                        incoming_date between now()::date and (Select now()::date + %s::integer)
                        """ %(is_warehouse_selected,warehouses, is_product_selected, products, analysis_days))
        incoming_dict = self._cr.dictfetchall()
        return incoming_dict

    def get_use_forecasted_sales_for_requisition(self):
        """
        Check the forecasting method from configuration
        :return: 1 or 0
        """
        self._cr.execute(
            """select value from ir_config_parameter where key='inventory_coverage_report_ept.use_forecasted_sales_for_requisition'""")
        is_forecast = self._cr.fetchall()

        if is_forecast and is_forecast[0][0] == 'True':
            return 1
        return 0

    def get_product_ads(self, products, warehouses, is_product_selected=False, is_warehouse_selected=False):
        """
        Get ads for selected or all products and warehouse wise.
        :param products: all selected products list
        :param warehouses: all selected warehouses list
        :param is_product_selected: Check products selected or all
        :param is_warehouse_selected: Check warehouses selected or all
        :return: [{'product_id':1234,'warehouse_id':1,'period_id':15,'ads':161.44}]
        Period id if use forecasted sales otherwise product_id and warehouse_id
        """
        select_column_list = """product_id, warehouse_id, period_id""" if self.get_use_forecasted_sales_for_requisition() == 1 else """product_id, warehouse_id"""
        query = """
                    SELECT
                        %s,
                        avg(ads) as ads 
                    FROM 
                        get_product_average_daily_sale
                    WHERE 
                        1 = case when %s = False then 1 else 
                                case when warehouse_id in %s then 1 else 0 end 
                            end
                        And  
                        1 = case when %s = False then 1 else 
                                case when product_id in %s then 1 else 0 end 
                            end    
                    group by %s""" % (
            select_column_list, is_warehouse_selected, warehouses, is_product_selected, products,
            select_column_list)
        self._cr.execute(query)
        ads = self._cr.dictfetchall()
        return ads

    def get_pending_moves(self, warehouses, products, is_warehouse_selected, is_product_selected):
        """
        Find the incomings which have past schedule date

        :param warehouses: warehouses list
        :param products: products list
        :param is_warehouse_selected: selected warehouses
        :param is_product_selected: selected products
        :return: moves [()]
        """
        warehouse_ids = warehouses and '(' + str(warehouses.ids).strip('[]') + ')' or False
        product_ids = products and '(' + str(products).strip('[]') + ')' or False
        query = """
                    SELECT
                    incoming_date,
                    product_id as product_id,
                    warehouse_id as warehouse_id,
                    incoming
                    FROM
                    get_incoming_data
                    WHERE
                        1 = case when %s = False then 1 else 
                                case when warehouse_id in %s then 1 else 0 end 
                            end
                        And  
                        1 = case when %s = False then 1 else 
                                case when product_id in %s then 1 else 0 end 
                            end
                    AND
                        incoming_date < now()::date
                    """ % (is_warehouse_selected, warehouse_ids, is_product_selected, product_ids)
        self._cr.execute(query)
        moves = self._cr.fetchall()
        return moves

    def get_recommandation_products(self):
        """
        Open Recommended report.
        :return: action with Recommended products
        """
        line_ids = self.get_products_for_requisition()
        tree_view_id = self.env.ref(
            'inventory_coverage_report_ept.view_tree_product_suggestion_line_ept').id
        report_action = {
            'name': 'Recommended Products',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'requisition.product.suggestion.line.ept',
            'context': self._context,
            'view_mode': 'tree,form',
            'views': [(tree_view_id, 'tree')],
            'domain': "[('id','in',%s)]" % line_ids.ids
        }
        return report_action

    def check_user_error(self, products, warehouses):
        """
        Check the user mistake and raise warning
        :param products:
        :param warehouses:
        :return:
        """
        # If not products selected and true the select product option.
        if not products and self.select_products:
            raise UserError(
                'You have select the choose products option and Products not selected..!')

        # If not any products in odoo which have a product type and can_be_used_for_coverage_report_ept
        if not self.select_products and not products:
            raise UserError(
                'No product type has been found for Storable product or Can Be Used For Coverage Report is not checked..!')

        # If not warehouses selected and True the select warehouse option.
        if self.select_warehouses and not warehouses:
            raise UserError(
                'You have select the choose warehouse option and Warehouses not selected..!')

        # If not any warehouses in odoo.
        if not self.select_warehouses and not warehouses:
            raise UserError('No any warehouses in odoo..!')

    def get_products_for_requisition(self):
        """
        Prepare data for the generate framing and
        Create recommandation report records if user want to open recommandation report
        :return:created records of requisition.product.suggestion.line.ept if this method call from recommandation report
        Otherwise True.
        """
        warehouse_obj = self.env['stock.warehouse']
        product_obj = self.env['product.product']
        warehouses = self.warehouse_ids
        products = self.product_ids
        inventory_analysis_days = self.inventory_analysis_of_x_days
        lines = self.mapped('product_suggestion_line_ids')
        lines.sudo().unlink()
        suggestion_line_ids = []

        if inventory_analysis_days <= 0:
            raise UserError(_("Please set proper Inventory Analysis of X days!!!"))
        inventory_analysis_start_date = fields.Date.context_today(self)
        inventory_analysis_end_date = self.get_next_date(inventory_analysis_start_date, days=inventory_analysis_days - 1)

        # if not warehouses:
        if not self.select_warehouses:
            warehouses = warehouse_obj.search([])

        # if not products:
        if not self.select_products:
            products = product_obj.search([('type', '=', 'product'), ('can_be_used_for_coverage_report_ept', '=', True)])

        self.check_user_error(products, warehouses)

        is_warehouse_selected = True if len(warehouses) > 0 else False
        is_product_selected = True if len(products) > 0 else False
        pending_pickings = self.get_pending_moves(warehouses, products and products.ids or [], is_warehouse_selected, is_product_selected)
        if pending_pickings:
            self.write({'has_pending_moves': True})

        self.prepare_main_frame(inventory_analysis_start_date, inventory_analysis_end_date,products.ids, warehouses.ids, inventory_analysis_days)
        if not self.inventory_coverage:
            product_suggestion_line_vals = []
            for product_id, line in report_frame.items():
                for frame_number, data in line.items():
                    if data.get('out_of_stock_percent', False):
                        warehouses = self.env['stock.warehouse'].browse(list(set([key[1] for key in report_frame.keys()])))
                        full_available, partially_available, full_available_warehouse_ids, partially_available_warehouse_ids  = self.check_product_stock_in_other_warehouses(product_id, warehouses, frame_number)
                        product_suggestion_line_vals.append(
                            {'product_id': product_id[0], 'warehouse_id': product_id[1],
                             'product_suggestion_id': self.id,
                             'supplier_id': data.get('sellers', False),
                             'procurement_source_warehouse_id': full_available_warehouse_ids and full_available_warehouse_ids[0] or partially_available_warehouse_ids and partially_available_warehouse_ids[0] or False})
            vals = [i for n, i in enumerate(product_suggestion_line_vals) if i not in product_suggestion_line_vals[n + 1:]]
            suggestion_line_ids = self.env['requisition.product.suggestion.line.ept'].create(vals)
        return suggestion_line_ids

    def write_header_in_worksheet(self, worksheet, headers, header_format, row):
        col = 0
        worksheet.set_row(row,40)
        for header in headers :
            if header in ['Product', 'Warehouse'] :
                worksheet.set_column(col, col, 17)
            else :
                worksheet.set_column(col, col, len(header) + 1)
            worksheet.write(row, col, header, header_format)
            col += 1
        worksheet.freeze_panes(row + 1, 0)

    def download_xlsx_report_with_text(self):
        """
        Generate execel report from report_frame
        :return: report
        """
        self.ensure_one()
        inventory_analysis_days = self.inventory_analysis_of_x_days
        inventory_analysis_start_date = fields.Date.context_today(self)
        inventory_analysis_end_date = self.get_next_date(inventory_analysis_start_date, days=inventory_analysis_days - 1)
        detail_report = self.show_detailed_report
        show_products = self.show_products
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        common_format_dict = {'font_name': 'Arial', 'font_size': 12, 'text_wrap': True}
        worksheet_format = workbook.add_format(common_format_dict)

        border_fmt = common_format_dict.copy()
        border_fmt.update({'border': True})
        border_format = workbook.add_format(border_fmt)

        right_align = common_format_dict.copy()
        right_align.update({'align': 'right', 'bg_color': 'e2e7e8'})
        right_align_fmt = workbook.add_format(right_align)

        left_align = common_format_dict.copy()
        left_align.update({'align': 'left', 'bg_color': 'e2e7e8'})
        left_align_fmt = workbook.add_format(left_align)

        center_align = common_format_dict.copy()
        center_align.update({'align': 'center', 'bg_color': 'e2e7e8'})
        center_align_fmt = workbook.add_format(center_align)

        title_format_dict = common_format_dict.copy()
        title_format_dict.update({'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'e2e7e8'})
        title_format = workbook.add_format(title_format_dict)

        header_format_dict = common_format_dict.copy()
        header_format_dict.update({'bold': True, 'bg_color': '0855da', 'align': 'center', 'valign': 'vcenter', 'font_size': 12, 'font_color': 'ffffff'})
        header_format = workbook.add_format(header_format_dict)

        out_stock_format_dict = common_format_dict.copy()
        out_stock_format_dict.update({'bg_color': 'fdc8cd', 'border': True})
        out_stock_format = workbook.add_format(out_stock_format_dict)

        product_format_dict = common_format_dict.copy()
        product_format_dict.update({'align': 'left', 'valign': 'vcenter', 'bg_color': 'e2e7e8', 'bold': True, 'border': True})
        product_format = workbook.add_format(product_format_dict)

        details = report_frame
        warehouses = self.env['stock.warehouse'].browse(list(set([key[1] for key in details.keys()])))
        product_obj = self.env['product.product']

        for warehouse_id in warehouses:
            warehouse = warehouse_id.name
            lines = {}
            headers = ['From Date', 'To Date', 'Days', 'Opening\nStock', 'Incoming', 'Average\nDaily Sale', 'Expected\nSales', 'Closing\nStock']
            if show_products == 'out_of_stock_product':
                title_string = "Inventory Coverage(Out Of Stock Products) : %s" % warehouse
                for key, value in details.items():
                    line = {k: v for k, v in value.items() if v.get('state', False) and v.get('state') == 'out_stock'}
                    if line:
                        lines.update({key: line})
            elif show_products == 'in_stock_product':
                title_string = "Inventory Coverage(In Stock Products) : %s" % warehouse
                for key, value in details.items():
                    line = {k: v for k, v in value.items() if v.get('state', False) and v.get('state') == 'in_stock'}
                    if line:
                        lines.update({key: line})
            else:
                lines.update(details)
                title_string = "Inventory Coverage : %s" % warehouse
                headers = ['From Date', 'To Date', 'Days', 'Opening\nStock', 'Incoming', 'Average\nDaily Sale', 'Expected\nSales', 'Closing\nStock']
            if self.check_stock_in_other_warehouses:
                headers += ['Available\nin Warehouses']
                headers += ['Partial Available\nin Warehouses']
            if not detail_report:
                headers = ['Incoming', 'Total Coverage\nDays', 'In Stock\nDays', 'Out of Stock\nDays']

            worksheet = workbook.add_worksheet(warehouse)
            worksheet.fit_width
            col = 0
            row = 0

            #worksheet.set_row(0, 40)

            if detail_report:
                worksheet.set_default_row(20)
                worksheet.merge_range(0, 0, 0, len(headers)-1, title_string, title_format)
                row += 1

                full_length = len(headers)-1
                remaining_length = full_length - 2
                worksheet.merge_range(row, 0, row, 1, "From Date : %s"%str(inventory_analysis_start_date), left_align_fmt)
                worksheet.merge_range(row, 2, row, remaining_length, "Report Date : %s"%datetime.strftime(datetime.today(), '%Y-%m-%d'), center_align_fmt)
                worksheet.merge_range(row, full_length - 1, row, full_length, "To Date : %s"%inventory_analysis_end_date, right_align_fmt)

                row += 1

                self.write_header_in_worksheet(worksheet, headers, header_format, row)
                row += 1
                worksheet.merge_range(row, 0, row, len(headers) - 1, '')
                row += 1
                line_count = 0
                for product_id, line in lines.items():
                    if not product_id[1] == warehouse_id.id:
                        continue
                    line_count += 1
                    product_data = product_obj.browse(product_id[0]).display_name + '   ---   ' + 'Current Stock: ' + str(details.get(product_id, {}).get(1.1, {}).get('opening_stock', 0.0))
                    worksheet.merge_range(row, 0, row, len(headers)-1, product_data, product_format)
                    row += 1
                    col = 0
                    for frame_number, data in SortedDict(line).items():
                        detail_data = [str(data.get('start_date')), str(data.get('end_date')),
                                       str(data.get('days')), round(data.get('opening_stock', 0.0), 0),
                                       round(data.get('incoming', 0.0), 2) or 0.0, round(data.get('ads', 0.0), 2),
                                       round(data.get('forecasted_sales', 0.0), 2), round(data.get('closing_stock', 0.0), 0)]
                        if self.check_stock_in_other_warehouses and data.get('state') == 'out_stock':
                            full_available, partially_available, full_available_warehouse_ids, partially_available_warehouse_ids = self.check_product_stock_in_other_warehouses(product_id, warehouses, frame_number)
                            detail_data += full_available if full_available else ['']
                            detail_data += partially_available if partially_available else ['']
                        col = 0
                        worksheet.write_row(row, col, detail_data, data.get('state') == 'out_stock' and show_products != 'out_of_stock_product' and out_stock_format or border_format)
                        row += 1
                    total_out_stock = sum([v.get('days', 0.0) for key, value in details.items() for k, v in value.items() if v.get('state') == 'out_stock' and key == product_id])#sum([value.get('days', 0.0) for key, value in line.items() if value.get('state') == 'out_stock'])
                    total_in_stock = sum([v.get('days', 0.0) for key, value in details.items() for k, v in value.items() if v.get('state') == 'in_stock' and key == product_id])#sum([value.get('days', 0.0) for key, value in line.items() if value.get('state') == 'in_stock'])
                    total_coverage_days = inventory_analysis_days

                    summary_data = "In Stock Days : " + str(total_in_stock) + "       " + "Out Of Stock Days : " + str(total_out_stock) + "       " + "Total Coverage Days : " + str(total_coverage_days)
                    worksheet.merge_range(row, 0, row, len(headers) - 1, summary_data, product_format)
                    row += 1
                    worksheet.set_row(row,8)
                    worksheet.merge_range(row, 0, row, len(headers) - 1, '')
                    row += 1
                self.set_column_width(workbook)
            else:
                headers = ['No', 'Product', 'Current Stock', 'incoming', 'Total Coverage Days', 'In Stock Days', 'Out of Stock Days']
                worksheet.merge_range(0, 0, 0, len(headers) - 1, title_string, title_format)
                row += 1

                full_length = len(headers)-1
                remaining_length = full_length - 2
                worksheet.merge_range(row, 0, row, 1, "From Date : %s"%str(inventory_analysis_start_date), left_align_fmt)
                worksheet.merge_range(row, 2, row, remaining_length, "Report Date : %s"%datetime.strftime(datetime.today(), '%Y-%m-%d'), center_align_fmt)
                worksheet.merge_range(row, full_length - 1, row, full_length, "To Date : %s"%inventory_analysis_end_date, right_align_fmt)

                row += 1

                self.write_header_in_worksheet(worksheet, headers, header_format, row)
                row += 1
                line_count = 0

                for product_id, line in lines.items():
                    if not product_id[1] == warehouse_id.id:
                        continue
                    line_count += 1
                    total_out_stock = sum([v.get('days', 0.0) for key, value in details.items() for k, v in value.items() if v.get('state') == 'out_stock' and key == product_id])#sum([value.get('days', 0.0) for key, value in line.items() if

                    total_in_stock = sum([v.get('days', 0.0) for key, value in details.items() for k, v in value.items() if v.get('state') == 'in_stock' and key == product_id])#sum([value.get('days', 0.0) for key, value in line.items() if

                    total_incoming = sum([value.get('incoming', 0.0) for key, value in line.items() if value.get('incoming')])
                    total_coverage_days = inventory_analysis_days
                    detail_data = [line_count,
                                   product_obj.browse(product_id[0]).display_name,
                                   details.get(product_id, {}).get(1.1, {}).get('opening_stock',0.0),
                                   total_incoming,
                                   total_coverage_days, total_in_stock, total_out_stock]

                    if details.get(product_id, {}).get(1.1, {}).get('opening_stock', 0.0) < 0:
                        worksheet.write_row(row, 0, detail_data, out_stock_format)
                    else:
                        worksheet.write_row(row, 0, detail_data, border_format)

                    row += 1
                worksheet.set_column(1, 1, 30)

        workbook.close()
        output.seek(0)
        output = base64.encodestring(output.read())
        self.write({'product_inventory_coverage_detail_file': output})
        filename = "Product_Recommendation_report_%s_to_%s.xlsx" % (inventory_analysis_start_date, inventory_analysis_end_date)
        if self.inventory_coverage:
            filename = "Inventory_Coverage_Report_%s_to_%s.xlsx" % (inventory_analysis_start_date, inventory_analysis_end_date)
        active_id = self.ids[0]
        self.clear_report_frame()
        return {
            'type' : 'ir.actions.act_url',
            'url': 'web/content/?model=requisition.product.suggestion.ept&field=product_inventory_coverage_detail_file&download=true&id=%s&filename=%s' % (active_id, filename),
            'target': 'new',
        }

    def clear_report_frame(self):
        """
        Clear report frame global dict
        :return:
        """
        report_frame.clear()
        return True

    def check_product_stock_in_other_warehouses(self, product_id, selected_warehouses, frame_number):
        """
            Find the stock in other warehouse at same time duration.
            :param product_id: (product_id, warehouse_id) i.e., (45203, 1)
            :param selected_warehouses: all selected warehouses for find stock
            :param frame_number: frame number i.e., 1.1 which have a out of stock
            :return: warehouse name in list with full_available, partially_available
        """
        data_frame = report_frame.get(product_id, {}).get(frame_number, {})
        #out of stock frame start date
        src_start_date = data_frame.get('start_date')

        #out of stock frme end date
        src_end_date = data_frame.get('end_date')

        #forecasted sales of out of stock frame
        forecasted_sales = data_frame.get('forecasted_sales', 0.0)

        # Find another warehouses
        warehouses = selected_warehouses.filtered(lambda x: x.id != product_id[1])

        full_available = []
        partially_available = []
        full_available_warehouse_ids = []
        partially_available_warehouse_ids = []

        for warehouse in warehouses:
            coverage = 0
            # key = frame no of the another warehouses
            # value = Data of the another warehouses like a 'opening_stock', 'closing_stock', start_date, end_date...
            for key, value in report_frame.get((product_id[0],warehouse.id), {}).items():
                # if not related frame than
                if math.floor(frame_number) != math.floor(key) or value.get('closing_stock', 0) < data_frame.get('ads', 0):
                    continue
                start_date = value.get('start_date')
                end_date = value.get('end_date')
                ### Fully Available in Stock
                if src_start_date >= start_date and src_end_date <= end_date and value.get('state') == 'in_stock' and forecasted_sales <= value.get('closing_stock', 0.0):
                    full_available.append(warehouse.name)
                    full_available_warehouse_ids.append(warehouse.id)
                    break

                elif (src_start_date >= start_date and src_start_date <= end_date) and value.get('state') == 'in_stock':
                    days = (end_date - src_start_date).days + 1
                    if days * data_frame.get('ads',0) > value.get('closing_stock',0):
                        is_fully_stock_available = False
                        if value.get('closing_stock', 0) > data_frame.get('ads', 0):
                            partially_available.append(warehouse.name)
                            partially_available_warehouse_ids.append(warehouse.id)
                        break
                    else:
                        coverage += days * data_frame.get('ads',0)

                elif (src_end_date >= start_date and src_end_date <= end_date) and value.get('state') == 'in_stock':
                    days = (src_end_date - start_date).days + 1
                    if days * data_frame.get('ads', 0) > value.get('closing_stock', 0):
                        if value.get('closing_stock', 0) > data_frame.get('ads',0):
                            partially_available.append(warehouse.name)
                            partially_available_warehouse_ids.append((warehouse.id))
                        break
                    else:
                        coverage += days * data_frame.get('ads',0)

            if warehouse.name not in partially_available and warehouse.name not in full_available and coverage >= forecasted_sales:
                full_available.append(warehouse.name)
                full_available_warehouse_ids.append(warehouse.id)

        return full_available, partially_available, full_available_warehouse_ids, partially_available_warehouse_ids

    def set_column_width(self, workbook):
        """
        set column width
        :param workbook: workbook data
        :return:
        """
        for worksheet in workbook.worksheets():
            if self.check_stock_in_other_warehouses:
                worksheet.set_column(0, 7, 10)
                worksheet.set_column(8, 9, 20)
            else:
                worksheet.set_column(0, 7, 15)
        return True

    def download_report_as_xlsx(self):
        """
        Download xlsx report and call framing creating function
        :return:xlsx report
        """
        self.ensure_one()
        self.inventory_coverage = True
        self.get_products_for_requisition()
        report_action = self.download_xlsx_report_with_text()
        return report_action

    def download_report(self):
        """
        call from inventory coverage download report button
        :return:
        """
        res = self.download_report_as_xlsx()
        return res

    def get_month_date_header_detail(self, start_date, end_date):
        d1_obj = datetime.strptime(str(start_date), "%Y-%m-%d")
        d2_obj = datetime.strptime(str(end_date), "%Y-%m-%d")
        res = []
        dt = d1_obj
        month_count = 0
        while dt <= d2_obj:
            res.append({'month_name':datetime.strftime(dt, '%B-%Y'), 'year':dt.year, 'start_date':dt.day})
            if dt.month != d2_obj.month :
                dt = datetime(dt.year, dt.month, 1) + relativedelta(months=1, days=-1)
            if dt.month == d2_obj.month:
                res[month_count].update({'end_date':d2_obj.day})
                break
            res[month_count].update({'end_date':dt.day})
            dt = dt + relativedelta(days=1)
            month_count += 1
        return res

class RequisitionProductSuggestionLine(models.TransientModel):
    _name = 'requisition.product.suggestion.line.ept'
    _description = "Inventory Coverage Report / Product Recommandation lines"
    _order = 'product_id, warehouse_id'

    product_suggestion_id = fields.Many2one('requisition.product.suggestion.ept')
    product_id = fields.Many2one('product.product', 'Product')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    procurement_source_warehouse_id = fields.Many2one('stock.warehouse', 'Procurement Source Warehouse')
