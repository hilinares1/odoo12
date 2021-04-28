from odoo import fields, models, api, _
from datetime import timedelta
import datetime
from odoo.exceptions import UserError, Warning
import math
from odoo.addons.inventory_coverage_report_ept.sortedcontainers.sorteddict import SortedDict

_state_tuple = [('draft', 'Draft'),
                ('generated', 'Calculated'),
                ('waiting', 'Waiting For Approval'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
                ('verified', 'Verified'),
                ('done', 'Done'),
                ('cancel', 'Cancelled')]
from odoo.addons.advance_purchase_ordering_ept.models.requisition_process_ept import _deliver_to_type 

class WarehouseRequisitionProcess(models.Model):
    _name = 'warehouse.requisition.process.ept'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Procurement Process"    
    _order = "requisition_date desc, id desc"

    def _compute_approval_buttons(self):
        for warehouse_process_id in self:
            show_approval_buttons = True if warehouse_process_id.is_approval_by_authorised and\
                                            warehouse_process_id.state == 'waiting' and\
                                            warehouse_process_id.approval_user_id.id == self._uid else False
            warehouse_process_id.show_approval_buttons = show_approval_buttons

    def _compute_is_approved_by_authorised(self):
        for record in self:
            record.is_approval_by_authorised = eval(self.env['ir.config_parameter'].sudo().get_param('advance_purchase_ordering_ept.approval_by_authorised', False))

    @api.model
    def get_default_approval_by_authorised(self):
        return eval(self.env['ir.config_parameter'].sudo().get_param('advance_purchase_ordering_ept.approval_by_authorised'))
    
    def default_is_use_forecast_sale_for_requisition(self):
        return eval(self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.use_forecasted_sales_for_requisition'))
        
    @api.model
    def get_default_date(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _set_purchase_order_count(self):
        for reorder in self:
            reorder.purchase_order_count = len(reorder.purchase_ids)

    def _set_sale_order_count(self):
        for reorder in self:
            reorder.sale_order_count = len(reorder.sale_ids)

    def _set_account_invoice_count(self):  
        for reorder in self:
            invoice_ids = self.env['account.invoice'].search([('intercompany_transfer_id', 'in', reorder.ict_ids.ids), ('type', 'in', ['out_invoice', 'out_refund'])])
            reorder.account_invoice_count = len(invoice_ids)

    def _set_supplier_invoice_count(self):
        for reorder in self:
            invoice_ids = self.env['account.invoice'].search([('intercompany_transfer_id', 'in', reorder.ict_ids.ids), ('intercompany_transfer_id', '!=', False), ('type', 'in', ['in_invoice', 'in_refund'])])
            reorder.supplier_invoice_count = len(invoice_ids)

    def _set_ict_count(self):
        for reorder in self:
            reorder.ict_count = len(reorder.ict_ids)

    def _set_picking_count(self):
        for reorder in self:
            picking_ids = self.env['stock.picking'].search([('intercompany_transfer_id', 'in', reorder.ict_ids.ids), ('intercompany_transfer_id', '!=', False)])
            reorder.picking_count = len(picking_ids)
            
    @api.model
    def get_default_past_sale_start_from(self):
        start_date = fields.Date.context_today(self)
        start_date_obj = str(start_date)
        return start_date_obj 

    name = fields.Char(string='Name', index=True, copy=False, default=lambda self: _('New'))
    show_approval_buttons = fields.Boolean(compute=_compute_approval_buttons)
    is_approval_by_authorised = fields.Boolean("Approval By Authorised", default=get_default_approval_by_authorised, copy=False)
    ict_count = fields.Integer(string='ICT Count', compute=_set_ict_count)
    sale_order_count = fields.Integer(string='Sale Order Count', compute=_set_sale_order_count)
    purchase_order_count = fields.Integer(string='Purchase Order Count', compute=_set_purchase_order_count)
    picking_count = fields.Integer(string='Picking Count', compute=_set_picking_count)
    account_invoice_count = fields.Integer(string='Account Invoice Count', compute=_set_account_invoice_count)
    is_use_forecast_sale_for_requisition = fields.Boolean("Use Forecast sale", default=default_is_use_forecast_sale_for_requisition, copy=False)
    supplier_invoice_count = fields.Integer(string='Supplier Invoice Count', compute=_set_supplier_invoice_count)
    requisition_date = fields.Date(string='Date', index=True, default=get_default_date)
    requisition_past_sale_start_from = fields.Date(string='Past Sales Start From', default=get_default_past_sale_start_from)
    reject_reason = fields.Text("Reject Reason")
    state = fields.Selection(_state_tuple, string='Status', default='draft', required=True, index=True, copy=False)
    deliver_to = fields.Selection(_deliver_to_type, string="Deliver To", default="general")
    user_id = fields.Many2one('res.users', string='Responsible User ', index=True, default=lambda self:self.env.uid)
    source_warehouse_id = fields.Many2one('stock.warehouse', string='Source Warehouse', index=True)
    approval_user_id = fields.Many2one('res.users', 'Authorised User', domain=lambda self:[('groups_id', '=', self.env.ref('advance_purchase_ordering_ept.group_approve_purchase_requisition_ept').id)])
    product_id = fields.Many2one(string="Requisition Process Products", related="warehouse_requisition_process_line_ids.product_id")
    warehouse_id = fields.Many2one(string="Warehouse", related="warehouse_configuration_line_ids.warehouse_id")
    warehouse_configuration_line_ids = fields.One2many('warehouse.requisition.configuration.line.ept', 'warehouse_requisition_process_id', string='Procurement Process Planning', copy=True)
    warehouse_requisition_process_line_ids = fields.One2many('warehouse.requisition.process.line.ept', 'warehouse_requisition_process_id', string='Warehouse Process Lines')
    warehouse_requisition_summary_ids = fields.One2many('warehouse.requisition.summary.line.ept', 'warehouse_requisition_process_id', string='Procurement Summary', copy=False)
    ict_ids = fields.One2many('inter.company.transfer.ept', 'warehouse_requisition_process_id', string='Inter Company Transactions')
    sale_ids = fields.One2many('sale.order', 'warehouse_requisition_process_id', string='Sales Order')
    purchase_ids = fields.One2many('purchase.order', 'warehouse_requisition_process_id', string='Purchase Order')
    picking_ids = fields.One2many('stock.picking', 'warehouse_requisition_process_id', string='Picking Lists')
    invoice_ids = fields.One2many('account.invoice', 'warehouse_requisition_process_id', string='Invoices')
    product_ids = fields.Many2many('product.product', string='Products')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence_id = self.env.ref('advance_purchase_ordering_ept.sequence_warehouse_requisition_process_ept').ids
            vals['name'] = sequence_id and self.env['ir.sequence'].browse(sequence_id).next_by_id() or 'New'
        return super(WarehouseRequisitionProcess, self).create(vals)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            mark_waiting = self._context.get('mark_requisition_as_waiting', False)
            mark_rejected = self._context.get('mark_requisition_as_rejected', False)
            order = self.browse([self._context['default_res_id']])
            if order.state == 'generated' and mark_waiting :
                order.state = 'waiting'
            if order.state == 'waiting' and mark_rejected :
                order.state = 'rejected'
                order.reject_reason = self._context.get('reject_reason', '')
        return super(WarehouseRequisitionProcess, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(WarehouseRequisitionProcess, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' : 
            if self._context.get('default_deliver_to') == 'general':
                warehouse_domain = []
                if warehouse_domain:
                    res['fields']['warehouse_configuration_line_ids']['views']['tree']['fields']['warehouse_id']['domain'] = warehouse_domain
                dest_warehouse_domain = []
                if dest_warehouse_domain:
                    res['fields']['warehouse_configuration_line_ids']['views']['tree']['fields']['destination_warehouse_id']['domain'] = dest_warehouse_domain
            source_domain = []
            if source_domain:
                res['fields']['source_warehouse_id']['domain'] = source_domain
        return res

    def action_cancel(self):
        """
        Cancel reorder
        :return:
        """
        return self.write({'state': 'cancel'})

    def action_draft(self):
        """
        Set to draft reorder
        :return:
        """
        line_ids = self.mapped('warehouse_requisition_process_line_ids')
        line_ids and line_ids.sudo().unlink()
        is_approve_by_authorized = self.get_default_approval_by_authorised()
        is_use_forecast_sale_for_requisition = self.default_is_use_forecast_sale_for_requisition()
        summary_line_ids = self.mapped('warehouse_requisition_summary_ids')
        summary_line_ids and summary_line_ids.sudo().unlink()
        return self.write({'state':'draft', 'is_approval_by_authorised':is_approve_by_authorized, 'is_use_forecast_sale_for_requisition':is_use_forecast_sale_for_requisition})

    def unlink(self):
        for reorder in self:
            if reorder and reorder.state == 'done':
                raise Warning("You can not delete transaction, if it is in Done state !!")
        res = super(WarehouseRequisitionProcess, self).unlink()
        return res

    def get_pending_moves(self, warehouse, product_ids=[]):
        """
        Find pending moves if find than not allow to reorder.
        :param warehouse:
        :param product_ids:
        :return:
        """
        product_ids = '(' + str(product_ids or self.product_ids and self.product_ids.ids or []).strip('[]') + ')'
        if product_ids:
            self._cr.execute("""SELECT sm.origin as origin, sp.name as name FROM stock_move sm 
                                JOIN stock_location ld ON ld.id = sm.location_dest_id
                                JOIN stock_warehouse whd ON ld.parent_path::text ~~ concat('%s', whd.view_location_id, '%s')
                                JOIN stock_picking sp ON sp.id = sm.picking_id
                                WHERE sm.date_expected::date < now()::date AND sm.state = 'assigned' AND sm.product_id in %s AND
                                ld.usage = 'internal' AND sm.warehouse_id = %s order by sm.date_expected
                            """
                             % ('%/', '/%', product_ids, warehouse.id))
            moves = self._cr.dictfetchall()
        return moves

    def action_confirm(self):
        """
        Confirm reorder and check the reorder required data
        :return:
        """
        line_obj = self.env['warehouse.requisition.process.line.ept']
        if not self.filtered(lambda x: x.product_ids):
            raise UserError(_("Please add some products!!!"))
        if not self.filtered(lambda x: x.warehouse_configuration_line_ids):
            raise UserError(_("Please select  Warehouse!!!!"))
        for warehouse_config_line in self.mapped('warehouse_configuration_line_ids'):
            pickings = self.get_pending_moves(warehouse_config_line.warehouse_id)
            if pickings:
                msg = """
                    You cannot confirm that process, because some pickings need to be rescheduled.!!! \n
                """
                for picking in pickings:
                    msg += " Picking => %s / Source Document => %s \n" % (picking.get('name', " "), picking.get('origin', " "))
                raise UserError(_(msg))
        
        if self.is_use_forecast_sale_for_requisition:
            list_of_period_ids = []
            warehouse_ids = []
            product_ids = self.product_ids.ids
            product_ids_str = '(' + str(product_ids or [0]).strip('[]') + ')'
            total_time = 0 
            for config_line in self.mapped('warehouse_configuration_line_ids'):
                warehouse_id = config_line.warehouse_id
                warehouse_ids.append(warehouse_id.id)
                total_time = config_line.requisition_estimated_delivery_time + config_line.requisition_backup_stock_days
                total = datetime.datetime.strptime(str(self.requisition_date), '%Y-%m-%d').date() + timedelta(days=int(total_time))
                list_of_period_ids = self.env['requisition.period.ept'].search([('date_start', '<=', total), ('date_stop', '>=', self.requisition_date)]).ids

            period_ids_str = '(' + str(list_of_period_ids or []).strip('[]') + ')'
            warehouse_ids_str = '(' + str(warehouse_ids or []).strip('[]') + ')'
            not_found_query = """
                    Select 
                        product.id as product_id, 
                        warehouse.id as warehouse_id,
                        period.id as period_id
                    From 
                        product_product product, stock_warehouse warehouse, requisition_period_ept period
                    Where 
                        product.id in %s And 
                        warehouse.id in %s And 
                        period.id in %s
                    
                    Except
                    
                    Select 
                        product_id, 
                        warehouse_id, 
                        period_id
                    from forecast_sale_ept
                    Where 
                        product_id in %s And 
                        warehouse_id in %s And 
                        period_id in %s
                        
                """ % (str(product_ids_str), str(warehouse_ids_str), str(period_ids_str) , str(product_ids_str), str(warehouse_ids_str), str(period_ids_str))
            self._cr.execute(not_found_query)
            res_dict = self._cr.dictfetchall()
            not_found_lines = [(0, 0, record) for record in res_dict]
            if not_found_lines:
                vals = {
                        'warehouse_requisition_process_id': self.id,
                        'mismatch_lines': not_found_lines,
                        'warehouse_ids': [(6, 0, warehouse_ids)]
                        }
                context = vals.copy()
                mismatch = self.env['mismatch.data.ept'].with_context(context).create(vals)
                if mismatch:
                    return mismatch.wizard_view()
        # optimize code
        create_lines_vals = [{
                                 'warehouse_requisition_process_id': warehouse_config_line.warehouse_requisition_process_id.id,
                                 'warehouse_configuraiton_line_id': warehouse_config_line.id,
                                 'product_id': product.id,
                                 'warehouse_id': warehouse_config_line.warehouse_id.id}
                             for product in self.product_ids
                             for warehouse_config_line in self.warehouse_configuration_line_ids
                             if self.deliver_to == 'general'
                             and not self.env['warehouse.requisition.process.line.ept'].search([('product_id', '=', product.id),
                                                                                                ('warehouse_configuraiton_line_id', '=', warehouse_config_line.id),
                                                                                                ('warehouse_requisition_process_id', '=', warehouse_config_line.warehouse_requisition_process_id.id),
                                                                                                ('warehouse_id', '=', warehouse_config_line.warehouse_id.id)])]
        line_obj.create(create_lines_vals)
        self._cr.commit()

    def clear_incoming_data(self):
        """
        Remove incoming data of the requisition process line
        :return:
        """
        if self.warehouse_requisition_process_line_ids:
            line_ids = '(' + str(self.warehouse_requisition_process_line_ids.ids).strip('[]') + ')'
            self._cr.execute("""DELETE FROM requisition_process_line_move_data where warehouse_requisition_process_line_id in %s """ % (line_ids))
            self._cr.commit()

    def remove_warehouse_requisition_summary_line_ept(self):
        """
        Remove summary line data
        :return:
        """
        ids = '(' + str(self.ids or []).strip('[]') + ')'
        if ids:
            self._cr.execute("""DELETE FROM warehouse_requisition_summary_line_ept where warehouse_requisition_process_id in %s""" % (ids))
            self._cr.commit()

    def action_calculate(self):
        """
           Calculate demand, expected sale, forecast sale, lead days sales
           :return:
       """
        ############################################################
        # Expected sales = sum(T2 forecast sales)                  #
        # forecasted_stock = closing of last frame of T1           #
        # Lead Days Sales = sum(Forecast sales of T1)              #
        # Demand Quantity = sum(T2 forecasted sales of 'out_stock')#
        # Demand never in negative                                 #
        # Instock Qty= sum(T2 forecast sales of 'in_stock')        #
        ############################################################
        confirm = self.action_confirm()
        if confirm:
            return confirm
        product_suggestion_obj = self.env['requisition.product.suggestion.ept']
        product_ids = self.warehouse_requisition_process_line_ids.mapped('product_id')
        forecast_stock_dict = {}
        lead_days_sales_dict = {}
        demand_dict = {}
        instock_dict = {}
        expected_dict = {}
        opening_stock_dict = {}
        # Delete all move data from requisition_process_line_ids of reorder
        self.clear_incoming_data()
        self.remove_warehouse_requisition_summary_line_ept()
        for config_line in self.warehouse_configuration_line_ids:
            # <====== Prepare t1 data =====>
            t1_start_date = self.requisition_date
            t1_end_date = config_line.schedule_date

            # Prepare t1 dict from ICR framing function
            # t1_dict format:
            # {(product_id, warehouse_id):{1.1:{'start_date': start_date, 'end_date': end_date, 'ads': ads qty,
            #                             'incoming':incoming qty, 'is_incoming': True /False, 'opening_stock': opening stock qty,
            #                             'closing_stock': closing stock qty, 'state': 'in_stock'/'out_stock',
            #                             'days': days, 'forecasted_sales': forecasted sales qty}}}
            product_suggestion_obj.clear_report_frame()
            t1_dict = product_suggestion_obj.prepare_main_frame(t1_start_date, t1_end_date, product_ids.ids, config_line.warehouse_id.ids, config_line.requisition_estimated_delivery_time)

            # Prepare forecast stock dict
            # add last closing
            forecast_stock_dict.update({product_id: SortedDict(frame_number).items()[-1][1].get('closing_stock', 0.0) for product_id, frame_number in t1_dict.items()})
            lead_days_sales_dict.update({product_id: round(sum([value.get('ads', 0.0) * value.get('days', 0.0) for frame, value in frame_number.items()], 0)) for product_id, frame_number in t1_dict.items()})
            opening_stock_dict.update({product_id: SortedDict(frame_number).items()[0][1].get('opening_stock', 0.0) for product_id, frame_number in t1_dict.items()})

            # clear inventory coverage global dict for t1_dict framing
            product_suggestion_obj.clear_report_frame()

            # <===== Prepare t2 data =====>
            t2_start_date = config_line.coverage_start_date
            t2_end_date = config_line.coverage_end_date
            # Prepare t2 dict from ICR framing function
            #t2_dict format:
            # {(product_id, warehouse_id):{1.1:{'start_date': start_date,
            #                             'end_date': end_date,
            #                             'ads': ads qty,
            #                             'incoming':incoming qty,
            #                             'is_incoming': True /False,
            #                             'opening_stock': opening stock qty,
            #                             'closing_stock': closing stock qty,
            #                             'state': 'in_stock'/'out_stock',
            #                             'days': days,
            #                             'forecasted_sales': forecasted sales qty}}}
            t2_dict = product_suggestion_obj.prepare_main_frame(t2_start_date, t2_end_date,
                                                                product_ids.ids,
                                                                config_line.warehouse_id.ids, config_line.requisition_backup_stock_days, forecast_stock_dict=forecast_stock_dict)

            # Prepare demand dict {(product_id, warehouse_id): Demand Qty}
            demand_dict.update({product_id: round(sum([value.get('ads', 0.0) * value.get('days', 0.0) for frame, value in frame_number.items() if value.get('state') == 'out_stock']), 0) for product_id, frame_number in t2_dict.items()})

            # Prepare instock dict {(product_id, warehouse_id): Instock Qty}
            instock_dict.update({product_id: round(sum([value.get('ads', 0.0) * value.get('days', 0.0) for frame, value in frame_number.items() if value.get('state') == 'in_stock']), 0) for product_id, frame_number in t2_dict.items()})

            # Prepare expected sales qty dict {(product_id, warehouse_id): expected sales qty}
            expected_dict.update({product_id: round(sum([value.get('ads', 0.0) * value.get('days', 0.0)  for frame, value in frame_number.items()]), 0) for product_id, frame_number in t2_dict.items()})

            # update forecast stock, lead days sales, expected sales, demand, opening stock in requisition process lines
            self.update_requisition_process_lines(forecast_stock_dict, lead_days_sales_dict, expected_dict, opening_stock_dict, demand_dict, instock_dict)
            self.update_move_data(t2_dict)

            # clear inventory coverage global dict for t2_dict framing
            product_suggestion_obj.clear_report_frame()

        self.write({'state': 'generated'})
        self.generate_summary()
        return True

    def update_requisition_process_lines(self, forecast_stock_dict, lead_days_sales_dict, expected_dict,opening_stock_dict, demand_dict, instock_dict):
        """
        update forecast stock, lead days sales, expected sales, demand, opening stock in requistion process lines
        :param forecast_stock_dict: {(product_id, warehouse_id): forecast stock qty}
        :param lead_days_sales_dict: {(product_id, warehouse_id): lead days sales qty}
        :param expected_dict: {(product_id, warehouse_id): expected sales qty}
        :param demand_dict: {(product_id, warehouse_id): demand qty}
        :param opening_stock_dict: {(product_id, warehouse_id): opening stock qty}
        :return:
        """
        # Prepare data for the update requisition process lines.
        # '(requisition_process_line_id, state, forecasted_stock_qty, qty_available_for_sale, expected_sales, requisition_qty, adjusted_requisition_qty)'
        vals = str([(
            line.id,
            'generated',
            round(forecast_stock_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(lead_days_sales_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(expected_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(instock_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(demand_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(opening_stock_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0),
            round(demand_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0)
            if round(demand_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0) > 0 and line.can_be_update else line.adjusted_requisition_qty if not line.can_be_update else 0.0
            ) for line in self.warehouse_requisition_process_line_ids] or []).strip('[]')

        if vals:
            # Update data of requisition process line with multiple records, fields and field values in one shot
            query = """update warehouse_requisition_process_line_ept as t set
                                state = c.state,
                                forecasted_stock = c.forecasted_stock,
                                qty_available_for_sale = c.qty_available_for_sale,
                                expected_sale = c.expected_sale,
                                warehouse_requisition_instock_qty = c.warehouse_requisition_instock_qty,
                                requisition_qty = c.requisition_qty,
                                opening_stock = c.opening_stock,
                                adjusted_requisition_qty = c.adjusted_requisition_qty
                            from (values
                                {}
                            ) as c(column_id, state, forecasted_stock, qty_available_for_sale, expected_sale, warehouse_requisition_instock_qty, requisition_qty, opening_stock, adjusted_requisition_qty) 
                            where c.column_id = t.id;""".format(vals)
            self._cr.execute(query)
            self._cr.commit()

        return True

    def update_move_data(self, t2_dict):
        """
        Set incoming moves in requisition_process_line_ids
        :param t2_dict: framing data
        :return:
        """
        # Find incoming products list
        products = list(set([key[0] for key, value in t2_dict.items() for k, v in value.items() if v.get('is_incoming', False)]))

        # Find incoming products warehouses
        warehouses = list(set([key[1] for key, value in t2_dict.items() for k, v in value.items() if v.get('is_incoming', False)]))

        if products and warehouses:
            product_ids = '(' + str(products).strip('[]') + ')'
            warehouse_ids = '(' + str(warehouses).strip('[]') + ')'

            # Insert new move data in requisition_process_line_ids
            query = """
                        INSERT INTO requisition_process_line_move_data
                        (move_id, schedule_date, quantity, warehouse_id, picking_id, product_id, warehouse_requisition_process_line_id)
                        SELECT move_id,schedule_date, quantity, warehouse_id, picking_id, product_id, 
                        (select id from warehouse_requisition_process_line_ept
                         WHERE product_id = t.product_id and warehouse_id = t.warehouse_id and warehouse_requisition_process_id = {})
                        FROM 
                        (SELECT move_id AS move_id, incoming_date AS schedule_date, incoming AS quantity, warehouse_id AS warehouse_id,
                         picking_id AS picking_id, product_id AS product_id  FROM get_incoming_data_with_move 
                         WHERE product_id in {} and warehouse_id in {})t
                     """.format(self.id, product_ids, warehouse_ids)
            self._cr.execute(query)
            self._cr.commit()
        return True

    def action_re_calculate(self):
        return self.action_calculate()

    def write(self, vals):
        """
        Recreate requisition summary when update adjusted_requisition_qty manually
        :param vals:
        :return:
        """
        result = super(WarehouseRequisitionProcess, self).write(vals)
        if 'warehouse_requisition_process_line_ids' in vals and list(filter(lambda v : isinstance(v[2], dict) and 'adjusted_requisition_qty' in v[2], vals['warehouse_requisition_process_line_ids'])):
            self.remove_warehouse_requisition_summary_line_ept()
            for record in self:
                record.generate_summary()
        return result

    def generate_summary(self):
        """
        Generate warehouse requisition summary
        :return:
        """
        self.ensure_one()
        summary_obj = self.env['warehouse.requisition.summary.line.ept']

        self._cr.execute("""
                        INSERT INTO warehouse_requisition_summary_line_ept
                        (warehouse_requisition_process_id, product_id, available_qty, requisition_qty, deliver_qty, is_sufficient_stock)
                        Select 
                        warehouse_requisition_process_id,
                        T.product_id as product_id, 
                        ware.stock as available_qty, 
                        requisition_qty, 
                        case when stock > requisition_qty then requisition_qty 
                        else 
                            case when stock < 0 then 0 else stock end 
                        end as deliver_qty ,
                        case when stock > requisition_qty then True
                        else False end as is_sufficient_stock
                        
                    from 
                    (
                        Select 
                            source_warehouse_id as warehouse_id, 
                            product_id, 
                            warehouse_requisition_process_id,
                            sum(adjusted_requisition_qty) as requisition_qty
                        from warehouse_requisition_process_line_ept line
                        INNER JOIN warehouse_requisition_process_ept process on process.id = line.warehouse_requisition_process_id 
                        WHERE warehouse_requisition_process_id = {}
                        GROUP BY source_warehouse_id, product_id, warehouse_requisition_process_id
                        HAVING sum(adjusted_requisition_qty) > 0
                    )T
                        INNER JOIN 
                    (
                            SELECT 
                                quant.product_id,
                                ware.id,
                                sum(quantity) as stock
                            FROM 
                                stock_quant quant 
                                    INNER JOIN stock_location loc ON loc.id = quant.location_id
                                    LEFT JOIN stock_warehouse ware ON loc.parent_path ~~ concat('%/',ware.view_location_id,'/%')
                            GROUP BY ware.id, quant.product_id
                    )ware
                        ON ware.id = T.warehouse_id and ware.product_id = T.product_id
                        """ .format(self.id))
        self._cr.commit()

        vals = str([(line.id, summary_obj.search([('product_id', '=', line.product_id.id), ('warehouse_requisition_process_id', '=', line.warehouse_requisition_process_id.id)]).id) for line in self.warehouse_requisition_process_line_ids if summary_obj.search([('product_id', '=', line.product_id.id), ('warehouse_requisition_process_id', '=', line.warehouse_requisition_process_id.id)])] or []).strip('[]')
        if vals:
            query = """
                    update warehouse_requisition_process_line_ept as t
                    set warehouse_requisition_summary_id = c.warehouse_requisition_summary_id
                    from (VALUES
                    {} 
                    ) AS c(column_id, warehouse_requisition_summary_id)
                    WHERE c.column_id = t.id
                    """.format(vals)
            self._cr.execute(query)
            self._cr.commit()

        self.generate_sharing_data()
        return True

    def generate_sharing_data(self):
        """
        Create product sharing data between warehouses
        :return:
        """
        warehouse_wise_product_share = self.get_product_sharing_details()
        vals = str([(line.id, warehouse_wise_product_share.get(line.warehouse_id.id).get(line.product_id.id)) for line in self.warehouse_requisition_process_line_ids if warehouse_wise_product_share.get(line.warehouse_id.id, {}).get(line.product_id.id, False)] or []).strip('[]')
        if vals:
            query = """
                    update warehouse_requisition_process_line_ept as t
                    set sharing_percent = c.sharing_percent
                    from
                    (values
                    {} 
                    ) as c(column_id, sharing_percent) 
                    where c.column_id = t.id""".format(vals)
            self._cr.execute(query)
            self._cr.commit()
        return True

    def get_product_sharing_details(self):
        self.ensure_one()
        warehouse_wise_product_share = {}
       
        group_wise_share_qry = """
            with order_line_calc as (
            Select 
                id,  warehouse_requisition_process_id, product_id, warehouse_id, qty_available_for_sale, expected_sale, 
                (adjusted_requisition_qty::Float) as TotalSales  
            from warehouse_requisition_process_line_ept 
            where warehouse_requisition_process_id = %s and adjusted_requisition_qty > 0
            )
            
            Select 
                product_id,
                warehouse_id,
                TotalSales as ads,
                case when (select sum(TotalSales) from order_line_calc where product_id = v.product_id) <= 0 then 0 else 
                round(cast(TotalSales / (select sum(TotalSales) from order_line_calc where product_id = v.product_id) * 100 as numeric),6) end as share_group
            from order_line_calc v
        """ % (str(self.id))
        self._cr.execute(group_wise_share_qry)
        res_dict = self._cr.dictfetchall()
        for dict_data in res_dict:
            prod_dict = warehouse_wise_product_share.get(dict_data['warehouse_id'], {})
            prod_dict.update({dict_data['product_id'] : (dict_data['share_group'] or 0.0)})
            warehouse_wise_product_share.update({dict_data['warehouse_id'] : prod_dict})

        return warehouse_wise_product_share

    def action_reject(self):
        ctx = self._context.copy()
        action = {
                'name': _('Reorder Reject Reason'),
                'view_mode': 'form',
                'res_model': 'requisition.reject.reason.ept',
                'view_id': self.env.ref('advance_purchase_ordering_ept.requisition_reject_reason_ept_form_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
                    }
        return action

    def action_approve(self):
        self.warehouse_requisition_process_line_ids.write({'state' : 'approved' })
        self.write({'state':'approved'})
        return True

    def action_update_requisition(self):
        self.write({'state': 'generated'})
        return True

    def action_verify(self):
        self.write({'state':'verified'})
        return True

    def action_requisition_email_sent(self, template_id):
        """
            Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env['mail.template'].browse(template_id)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='warehouse.requisition.process.ept',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            custom_layout="advance_purchase_ordering_ept.mail_template_data_notification_email_requisition",
            force_email=True
        )
        
        mark_waiting = self._context.get('mark_requisition_as_waiting', False)
        mark_rejected = self._context.get('mark_requisition_as_rejected', False)
        if mark_waiting:
            ctx.update({'mark_requisition_as_waiting': mark_waiting})
        if mark_rejected : 
            ctx.update({'mark_requisition_as_rejected': mark_rejected,
                        'reject_reason':self._context.get('reject_reason', '')
                        })
        
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def reject_warehouse_requisition_with_reason(self, reason):
        approval_by_authorised = self.is_approval_by_authorised
        send_email = eval(self.env['ir.config_parameter'].sudo().get_param('advance_purchase_ordering_ept.requisition_send_email'))
        reject_email_template_id = self.env.ref('advance_purchase_ordering_ept.mail_template_warehouse_reqisition_reject_ept').id
        action = {}
        if approval_by_authorised and send_email:
            if not reject_email_template_id:
                raise (_("Email Template for Reject not Found !!!"))
            action = self.with_context(mark_requisition_as_rejected=True, reject_reason=reason).action_requisition_email_sent(reject_email_template_id)
        else:
            self.write({'state':'rejected', 'reject_reason':reason})
        return action

    def action_request_for_approval(self):
        self.ensure_one()
        approval_by_authorised = self.is_approval_by_authorised
        send_email = eval(self.env['ir.config_parameter'].sudo().get_param('advance_purchase_ordering_ept.requisition_send_email'))
        approve_email_template_id = self.env.ref('advance_purchase_ordering_ept.mail_template_warehouse_reqisition_approve_ept').id
        action = {}
        if approval_by_authorised and send_email:
            if not approve_email_template_id :
                raise UserError(_("Email Template for Request For Approval not Found !!!"))
            if not self.approval_user_id :
                raise UserError(_("Please set Authorised User For Procurement Process !!!."))
            action = self.with_context(mark_requisition_as_waiting=True).action_requisition_email_sent(approve_email_template_id)
        else :
            self.write({'state':'waiting'})
        return action

    def action_view_sale_order(self):
        form_view_id = self.env.ref('sale.view_order_form').id
        tree_view_id = self.env.ref('sale.view_order_tree').id
        resource_ids = self.sale_ids.ids
        action = {
            'name': _('Sale Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'target': 'current',
            'domain': "[('id','in',%s)]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def action_view_ICT_order(self):
        form_view_id = self.env.ref(
            'intercompany_transaction_ept.inter_company_transfer_ept_form_view').id
        tree_view_id = self.env.ref(
            'intercompany_transaction_ept.inter_company_transfer_ept_tree_view').id
        resource_ids = self.ict_ids.ids
        action = {
            'name': _('ICT Order'),
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_model': 'inter.company.transfer.ept',
            'domain': "[('id','in',%s)]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def action_view_purchase_order(self):
        tree_view_id = self.env.ref('purchase.purchase_order_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        resource_ids = self.purchase_ids.ids
        action = {
            'name': _('Purchase Order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'target':'current',
            'domain':"[('id','in',%s)]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def action_view_invoices(self):
        tree_view_id = self.env.ref('account.invoice_tree').id
        form_view_id = self.env.ref('account.invoice_form').id
        resource_ids = self.ict_ids.ids
        action = {
            'name': _('Customer Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'target':'current',
            'domain':"[('intercompany_transfer_id','in',%s),('type','in',['out_invoice','out_refund'])]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def action_view_supplier_invoices(self):
        tree_view_id = self.env.ref('account.invoice_supplier_tree').id
        form_view_id = self.env.ref('account.invoice_supplier_form').id
        resource_ids = self.ict_ids.ids
        action = {
            'name': _('Supplier Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'target':'current',
            'domain':"[('intercompany_transfer_id','in',%s),('intercompany_transfer_id','!=',False),('type','in',['in_invoice','in_refund'])]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def action_view_picking(self):
        form_view_id = self.env.ref('stock.view_picking_form').id
        tree_view_id = self.env.ref('stock.vpicktree').id
        resource_ids = self.ict_ids.mapped('picking_ids').ids
        action = {
            'name': _('Pickings'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'target': 'current',
            'domain': "[('id','in',%s),('id','!=',False)]" % (resource_ids),
        }
        return self._open_form_tree_view(action, form_view_id, tree_view_id, resource_ids)

    def _open_form_tree_view(self, action, form_view_id, tree_view_id, resource_ids):
        if len(resource_ids) == 1:
            action.update({'view_id': form_view_id,
                           'res_id': resource_ids[0],
                           'view_mode': 'form'})
        else:
            action.update({'view_id': False,
                           'view_mode': 'tree,form',
                           'views': [(tree_view_id, 'tree'), (form_view_id, 'form')]})

        return action

    def action_transfer(self):
        """
        Create transfer if warehouses is same company otherwise create Intercompany transfer
        :return:
        """
        self.ensure_one()
        ict_obj = self.env['inter.company.transfer.ept']
        summary_obj = self.env['warehouse.requisition.summary.line.ept']
        warehouse_process_line_obj = self.env['warehouse.requisition.process.line.ept']
        dest_warehouse_wise_ict_order = {}
        
        ict_order_wise_product_qty = {}
        for summary_id in self.warehouse_requisition_summary_ids.ids:
            summary = summary_obj.browse(summary_id)
            if summary.available_qty > 0:
                for line_id in summary.warehouse_requisition_process_line_ids.filtered(lambda x: x.adjusted_requisition_qty > 0).ids:
                    line = warehouse_process_line_obj.browse(line_id)
                    product = summary.product_id
                    if not line.warehouse_configuraiton_line_id.is_create_intercompany_transfer():
                        continue
                                       
                    dest_warehouse_id = line.warehouse_configuraiton_line_id.destination_warehouse_id
                    avail_qty = round(summary.deliver_qty * line.sharing_percent / 100, 0)
                    ICT_order = dest_warehouse_wise_ict_order.get(dest_warehouse_id.id, '')
                    if not ICT_order:
                        order_vals = {}
                        if self.source_warehouse_id.id == dest_warehouse_id.id:
                            continue
                        if self.source_warehouse_id.company_id.id != dest_warehouse_id.company_id.id:
                            order_vals = self.prepare_ict_order_vals(line.warehouse_configuraiton_line_id, ict_type='ict')
                        else:
                            order_vals = self.prepare_ict_order_vals(line.warehouse_configuraiton_line_id, ict_type='internal')
                        if order_vals :
                            ICT_order = ict_obj.create(order_vals)
                            ICT_order.write({'pricelist_id': ICT_order.destination_company_id.sudo().partner_id.sudo().property_product_pricelist.id,
                                             'crm_team_id':ICT_order.destination_company_id.sudo().partner_id.sudo().team_id.id})
                            dest_warehouse_wise_ict_order.update({dest_warehouse_id.id:ICT_order})
                        else :
                            continue
                    line.warehouse_configuraiton_line_id.write({'intercompany_transfer_id': ICT_order.id})
                    if ict_order_wise_product_qty.get(ICT_order, ''):
                        if product in ict_order_wise_product_qty[ICT_order]:
                            ict_order_wise_product_qty[ICT_order][product] += avail_qty
                        else :
                            ict_order_wise_product_qty[ICT_order].update({product:avail_qty})
                    else :
                        ict_order_wise_product_qty.update({ICT_order: {product: avail_qty}})
            
        for ict_order in ict_order_wise_product_qty :
            lines = [(0, 0, self.prepare_ict_order_line_vals(ict_order, product, ict_order_wise_product_qty[ict_order][product])) for product in ict_order_wise_product_qty[ict_order]]
            order_vals = {'warehouse_requisition_process_id': self.id, 'intercompany_transferline_ids': lines}
            ict_order.write(order_vals)
        self.write({'state': 'done'})
        return True

    def prepare_ict_order_vals(self, warehouse_configuraiton_line, ict_type):
        self.ensure_one()
        dest_warehouse = warehouse_configuraiton_line.get_warehouse_for_ict()

        ict_obj = self.env['inter.company.transfer.ept'].with_context(force_company=dest_warehouse.company_id.id)

        new_record = ict_obj.new({'source_warehouse_id':self.source_warehouse_id.id,
                                  'source_company_id':self.source_warehouse_id.company_id.id,
                                  'destination_warehouse_id':dest_warehouse.id,
                                  'destination_company_id':dest_warehouse.company_id.id,
                                  'type': ict_type})
                                       
        new_record.source_warehouse_id_onchange()
        new_record.onchange_destination_warehouse_id()
        vals = new_record._convert_to_write(new_record._cache)
        return vals

    def prepare_ict_order_line_vals(self, ict_order, product, ordered_qty):
        self.ensure_one()
        ict_order_line_obj = self.env['inter.company.transfer.line.ept']
        order_line_data = {'product_id': product.id,
                           'inter_transfer_id': ict_order.id,
                           'quantity': ordered_qty,
                            }
        order_line = ict_order_line_obj.new(order_line_data)
        order_line.default_price_get()
        vals = order_line._convert_to_write(order_line._cache)
        return vals
