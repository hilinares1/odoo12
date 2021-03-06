from odoo import models, fields, api


class ProductAverageDailySale(models.Model):
    _name = "product.average.daily.sale"
    _description = "Product average daily sale"

    period_id = fields.Many2one('requisition.period.ept', string='Period')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    product_id = fields.Many2one('product.product', string='Products')
    ads = fields.Float('Average Daily Sale')
    monthly_sale = fields.Float('Monthly Sales')
    monthly_days = fields.Float('Monthly Days')
    period_start_date = fields.Date('Period Start Date')
    period_stop_date = fields.Date('Period Stop Date')
    type = fields.Selection([('forecasted_sales', 'Forecasted Sales'),
                             ('actual_past_sales', 'Actual Past Sales')], string='ADS Type')

    @api.model
    def create_stored_procedures(self):
        query = """
            CREATE OR REPLACE FUNCTION public.add_update_product_ads_data()
            RETURNS VOID AS
            $BODY$  
                DECLARE 
                    is_forecast_in_use INTEGER := 0; 
                    past_sale_days text := '';
                    beginning_date date;
                    period_date_start date;
            BEGIN
                Drop table if exists ads_table_data;
                Create TEMPORARY TABLE ads_table_data(
                    p_id integer, 
                    w_id integer, 
                    per_id integer, 
                    dt_start date, 
                    dt_stop date, 
                    total_sale decimal, 
                    month_day integer, 
                    average_sale decimal,
                    type text
                );
                is_forecast_in_use :=  (Select case when value = 'True' then 1 else 0 end From ir_config_parameter Where key = 'inventory_coverage_report_ept.use_forecasted_sales_for_requisition');
                beginning_date := (Select now()::date - (Select value From ir_config_parameter Where key = 'inventory_coverage_report_ept.requisition_sales_past_days')::integer);
                period_date_start := (select date_start from requisition_period_ept where date_start <= beginning_date order by date_start desc limit 1);
                
                IF is_forecast_in_use = 1 Then
                    -- Use forecasted sales
                    Insert into ads_table_data
                    Select 
                        product_id,
                        warehouse_id,
                        period_id, 
                        date_start,
                        date_stop,
                        sum(forecast_sales) total_sales,
                        max(month_days) as month_days,
                        round(sum(forecast_sales) / max(month_days),2) as ads ,
                        'forecasted_sales'::text as type 
                        
                    From
                    (
                        
                        Select 
                            product_id ,
                            warehouse_id,
                            period.id as period_id,
                            period.date_start,
                            period.date_stop,
                            sale.forecast_sales::decimal as forecast_sales,
                            (date_stop- date_start) + 1 as month_days
                        From
                            forecast_sale_ept sale 
                                Inner Join stock_warehouse ware ON ware.id = sale.warehouse_id
                                Inner Join requisition_period_ept period on period.id = sale.period_id
                        Where period.date_stop >= now()
                    )Data
                    Group by product_id, warehouse_id, period_id,date_start,date_stop;	
                    
                    Delete from product_average_daily_sale where period_stop_date >= now();
                ELSE
                    -- Use past actual sales
                    Insert into ads_table_data
                    Select
                        product_id,
                        warehouse_id,
                        period_id, 
                        period.date_start,
                        period.date_stop,
                        sum(product_uom_qty) total_sales,
                        max(month_days) as month_days,
                        round(sum(product_uom_qty) / max(month_days),2) as ads,
                        'actual_past_sales'::text as type
                    From 
                    (
                        Select 
                            product_id ,
                            warehouse_id,
                            period.id as period_id,
                            product_uom_qty,
                            (date_stop- date_start) + 1 as month_days
                        from 
                        (
                            Select 
                                move.product_id,
                                coalesce(move.warehouse_id,ware.id) as warehouse_id,
                                move.date as move_date,
                                move.product_uom_qty as product_uom_qty
                            From
                                stock_move move 
                                    Inner Join Stock_location source on source.id = move.location_id
                                    Inner Join stock_location dest on dest.id = move.location_dest_id
                                    LEFT JOIN stock_warehouse ware ON source.parent_path::text ~~ concat('%/', ware.view_location_id, '/%')
                                    
                            Where move.state = 'done' and source.usage = 'internal' and dest.usage='customer' and move.date >= period_date_start
            
                            Union All
            
                            Select 
                                move.product_id,
                                coalesce(move.warehouse_id,ware.id) as warehouse_id,
                                move.date as move_date,
                                move.product_uom_qty * -1 as product_uom_qty
                                
                            From
                                stock_move move 
                                    Inner Join Stock_location source on source.id = move.location_id
                                    Inner Join stock_location dest on dest.id = move.location_dest_id
                                    LEFT JOIN stock_warehouse ware ON dest.parent_path::text ~~ concat('%/', ware.view_location_id, '/%')


                            Where move.state = 'done' and source.usage = 'customer' and dest.usage='internal' and move.date >= period_date_start
                        )T
                        Left Join 
                            requisition_period_ept period on 
                                date_trunc('month',period.date_start)::date = date_trunc('month',move_date)::date and 
                                date_trunc('year',period.date_start)::date = date_trunc('year',move_date)::date 
                    )Data
                        Inner Join requisition_period_ept period on period.id = Data.period_id
                    Group by product_id, warehouse_id, period_id,period.date_start,period.date_stop;   
                    
                    Delete from product_average_daily_sale 
                    where period_id in (select distinct per_id from ads_table_data where per_id in (select distinct id from requisition_period_ept where date_start >= period_date_start and date_start <= now()::date));     
                End IF;
                
                INSERT INTO product_average_daily_sale (period_id, warehouse_id, product_id, ads, monthly_sale, 
                    monthly_days, period_start_date, period_stop_date, type, create_uid, create_date, write_uid, write_date)
                select per_id, w_id, p_id, average_sale, total_sale, month_day, dt_start, dt_stop, type,1, now()::date, 1,now()::date from ads_table_data;
            
            END;
            $BODY$
              LANGUAGE plpgsql VOLATILE
              COST 100;
            """
        self._cr.execute(query)
        return True

    def calculate_average_daily_sales_using_cron(self):
        self.create_stored_procedures()
        query="select add_update_product_ads_data();"
        self._cr.execute(query)
        return True
