from odoo import fields, models, api, _
from datetime import timedelta
import datetime
from odoo.exceptions import UserError, Warning
import logging
from odoo.addons.inventory_coverage_report_ept.sortedcontainers.sorteddict import SortedDict
_logger = logging.getLogger(__name__)

_state_tuple = [('draft', 'Draft'),
                ('generated', 'Calculated'),
                ('waiting', 'Waiting For Approval'),
                ('approved', 'Approved'),
                ('rejected', 'Rejected'),
                ('verified', 'Verified'),
                ('done', 'Done'),
                ('cancel', 'Cancelled')]

_deliver_to_type = [('general', 'General')]

class RequisitionProcess(models.Model):
    _name = 'requisition.process.ept'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Reorder Process"
    _order = 'requisition_date desc, id desc'

    @api.model
    def get_default_approval_by_authorised(self):
        return eval(self.env['ir.config_parameter'].sudo().get_param(
            'advance_purchase_ordering_ept.approval_by_authorised'))

    @api.model
    def get_default_date(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def _set_purchase_order_count(self):
        for reorder in self:
            reorder.purchase_order_count = len(reorder.purchase_order_ids)

    @api.model
    def get_default_past_sale_start_from(self):
        start_date = fields.Date.context_today(self)
        return str(start_date)

    def _compute_approval_buttons(self):
        for requisition_id in self:
            requisition_id.show_approval_buttons = True if requisition_id.is_approval_by_authorised and requisition_id.state == 'waiting' and requisition_id.approval_user_id.id == self._uid else False

    def _compute_is_approved_by_authorised(self):
        for record in self:
            record.is_approval_by_authorised = eval(
                self.env['ir.config_parameter'].sudo().get_param(
                    'advance_purchase_ordering_ept.approval_by_authorised', False))

    def default_is_use_forecast_sale_for_requisition(self):
        return eval(self.env['ir.config_parameter'].sudo().get_param(
            'inventory_coverage_report_ept.use_forecasted_sales_for_requisition'))

    name = fields.Char(string='Name', index=True, copy=False, default=lambda self: _('New'))
    is_approval_by_authorised = fields.Boolean("Approval By Authorised",
                                               default=get_default_approval_by_authorised,
                                               copy=False)
    is_use_forecast_sale_for_requisition = fields.Boolean("Use Forecast sale For Requisition",
                                                          default=default_is_use_forecast_sale_for_requisition,
                                                          copy=False)
    show_approval_buttons = fields.Boolean(compute=_compute_approval_buttons)

    purchase_order_count = fields.Integer(string='Purchase Order Count',
                                          compute=_set_purchase_order_count)

    requisition_date = fields.Date(string='Date', index=True, default=get_default_date)
    requisition_past_sale_start_from = fields.Date(string='Past Sales Start From',
                                                   default=get_default_past_sale_start_from)

    state = fields.Selection(_state_tuple, string='Status', default='draft', index=True, copy=False,
                             track_visibility="onchange")
    deliver_to = fields.Selection(_deliver_to_type, string="Deliver To", default="general")

    reject_reason = fields.Text("Reject Reason")

    partner_id = fields.Many2one('res.partner', string='Vendor', index=True)
    user_id = fields.Many2one('res.users', string='Responsible User ', index=True,
                              default=lambda self: self.env.uid,
                              help="Resposible user for Reorder process")
    company_id = fields.Many2one('res.company', string='Company', index=True,
                                 default=lambda self: self.env.user.company_id)
    approval_user_id = fields.Many2one('res.users', 'Authorised User', domain=lambda self: [(
                                                                                            'groups_id',
                                                                                            '=',
                                                                                            self.env.ref(
                                                                                                'advance_purchase_ordering_ept.group_approve_purchase_requisition_ept').id)],
                                       help="Authorized user to approve/reject Reorder process ")
    warehouse_id = fields.Many2one('stock.warehouse', related='configuration_line_ids.warehouse_id',
                                   string='Warehouse')
    product_id = fields.Many2one('product.product',
                                 related='requisition_process_line_ids.product_id',
                                 string='Product')

    configuration_line_ids = fields.One2many('requisition.configuration.line.ept',
                                             'requisition_process_id', string='Reorder Planning',
                                             copy=True)
    requisition_process_line_ids = fields.One2many('requisition.process.line.ept',
                                                   'requisition_process_id',
                                                   string='Reorder Process Calculation')
    requisition_summary_ids = fields.One2many('requisition.summary.line.ept',
                                              'requisition_process_id', string='Reorder Summary',
                                              copy=False)
    purchase_order_ids = fields.One2many('purchase.order', 'requisition_process_id',
                                         string='Purchase Orders')
    product_ids = fields.Many2many('product.product', string='Products')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence_id = self.env.ref(
                'advance_purchase_ordering_ept.sequence_requisition_process').ids
            if sequence_id:
                record_name = self.env['ir.sequence'].browse(sequence_id).next_by_id()
            else:
                record_name = 'New'
            vals['name'] = record_name
        result = super(RequisitionProcess, self).create(vals)
        return result

    def write(self, vals):
        result = super(RequisitionProcess, self).write(vals)
        if 'requisition_process_line_ids' in vals and list(
                filter(lambda v: isinstance(v[2], dict) and 'adjusted_requisition_qty' in v[2],
                       vals['requisition_process_line_ids'])):
            self.remove_requisition_summary_line_ept()
            for requisition_id in self:
                requisition_id.generate_summary()
        return result

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        supplier_id = self.partner_id and self.partner_id.id or False
        domain = {'product_ids': [('type', '=', 'product'),
                                  ('can_be_used_for_coverage_report_ept', '=', True)]}
        res = {'domain': domain}
        product_ids = []
        self.product_ids = [(6, 0, [])]
        if supplier_id:
            supplierinfos = self.env['product.supplierinfo'].search(
                [('name', 'child_of', supplier_id)])
            for supplierinfo in supplierinfos:
                if supplierinfo.product_tmpl_id and supplierinfo.product_tmpl_id.product_variant_ids:
                    product_ids.extend(supplierinfo.product_tmpl_id.product_variant_ids.ids)
        domain['product_ids'].append(('id', 'in', product_ids))
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(RequisitionProcess, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            if self._context.get('default_deliver_to') == 'general':
                warehouse_domain = []
                if warehouse_domain:
                    res['fields']['configuration_line_ids']['views']['tree']['fields'][
                        'warehouse_id']['domain'] = warehouse_domain
                dest_warehouse_domain = []
                if dest_warehouse_domain:
                    res['fields']['configuration_line_ids']['views']['tree']['fields'][
                        'destination_warehouse_id']['domain'] = dest_warehouse_domain
        return res


    def generate_summary(self):
        self.ensure_one()
        res = {}
        res_dict = {}
        summary_obj = self.env['requisition.summary.line.ept']

        partner_ids = '(' + str([self.partner_id.id] or []).strip('[]') + ')'
        child_partner = '(' + str(self.partner_id.child_ids.ids if self.partner_id.child_ids else self.partner_id.id or []).strip('[]') + ')'
        query = """
                    INSERT INTO requisition_summary_line_ept
                    (requisition_process_id, product_id, minimum_requisition_qty, requisition_qty, po_qty, supplier_rule_satisfied)
                    Select 
                        requisition_process_id,
                        T.product_id as product_id, 
                        info.min_stock as minimum_requisition_qty,
                        requisition_qty,
                        case when info.min_stock < requisition_qty then requisition_qty else info.min_stock end as po_qty, 
                        case when info.min_stock > requisition_qty then 'f'::boolean else 't'::boolean end as supplier_rule_satisfied
                    from 
                    (
                        Select 
                        product_id,
                        pt.id as product_tmpl_id,
                        requisition_process_id,
                        sum(adjusted_requisition_qty) as requisition_qty
                        from requisition_process_line_ept line
                        Inner JOin requisition_process_ept process on process.id = line.requisition_process_id
                        INNER JOIN product_product pp ON pp.id = line.product_id
                        INNER JOIN product_template pt ON pt.id =  pp.product_tmpl_id
                        where requisition_process_id = {}
                        group by product_id, requisition_process_id, pt.id
                        having sum(adjusted_requisition_qty) > 0
                    )T
                        Inner Join
                     (
                             Select
                                 si.product_id,
                                si.product_tmpl_id,
                                 min(min_qty) as min_stock
                             from
                                 product_supplierinfo si
                                where name in {} or name in {}
                    
                             group by si.product_id, si.product_tmpl_id
                     )info
                      on CASE WHEN info.product_id IS NOT NULL THEN info.product_id = T.product_id ELSE info.product_tmpl_id = T.product_tmpl_id END
                    """.format(self.id, partner_ids, child_partner)
        self._cr.execute(query)
        self._cr.commit()

        vals = str([(line.id, summary_obj.search([('product_id', '=', line.product_id.id), ('requisition_process_id', '=', line.requisition_process_id.id)]).id) for line in self.requisition_process_line_ids if summary_obj.search([('product_id', '=', line.product_id.id), ('requisition_process_id', '=', line.requisition_process_id.id)])] or []).strip('[]')
        if vals:
            query = """
                        update requisition_process_line_ept as t
                        set requisition_summary_id = c.requisition_summary_id
                        from (VALUES
                        {} 
                        ) AS c(column_id, requisition_summary_id)
                        WHERE c.column_id = t.id
                    """.format(vals)
            self._cr.execute(query)
            self._cr.commit()
        self.generate_sharing_data()
        return True

    def remove_requisition_summary_line_ept(self):
        summary_obj = self.env['requisition.summary.line.ept']
        ids = '(' + str(self.ids or []).strip('[]') + ')'
        if ids:
            self._cr.execute("""DELETE FROM requisition_summary_line_ept where requisition_process_id in %s""" % (ids))
            self._cr.commit()


    def generate_sharing_data(self):
        warehouse_wise_product_share = self.get_product_sharing_details()
        vals = str([(line.id,
                     warehouse_wise_product_share.get(line.warehouse_id.id).get(line.product_id.id))
                    for line in self.requisition_process_line_ids if
                    warehouse_wise_product_share.get(line.warehouse_id.id, {}).get(
                        line.product_id.id, False)] or []).strip('[]')
        if vals:
            query = """update requisition_process_line_ept as t
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

        group_wise_share_qty = """
            with order_line_calc as (
            Select 
                id,  requisition_process_id, product_id, warehouse_id, qty_available_for_sale, expected_sale, 
                (adjusted_requisition_qty::Float) as TotalSales  
            from requisition_process_line_ept 
            where requisition_process_id = %s and adjusted_requisition_qty > 0
            )
            
            Select 
                product_id,
                warehouse_id,
                TotalSales as ads,
                case when (select sum(TotalSales) from order_line_calc where product_id = v.product_id) <= 0 then 0 else 
                round(cast(TotalSales / (select sum(TotalSales) from order_line_calc where product_id = v.product_id) * 100 as numeric),6) end as share_group
            from order_line_calc v
        """ % (str(self.id))
        self._cr.execute(group_wise_share_qty)
        res_dict = self._cr.dictfetchall()

        for dict_data in res_dict:
            prod_dict = warehouse_wise_product_share.get(dict_data['warehouse_id'], {})
            prod_dict.update({dict_data['product_id']: (dict_data['share_group'] or 0.0)})
            warehouse_wise_product_share.update({dict_data['warehouse_id']: prod_dict})

        return warehouse_wise_product_share

    def clear_incoming_data(self):
        """
        Clear incoming data when generate demand
        :return:
        """
        # Delete all move data from requisition_process_line_ids of reorder
        if self.requisition_process_line_ids:
            line_ids = '(' + str(self.requisition_process_line_ids.ids).strip('[]') + ')'
            self._cr.execute("""DELETE FROM requisition_process_line_move_data where requisition_process_line_id in %s """ % (line_ids))
            self._cr.commit()

    def action_calculate(self):
        """
        Calculate demand, expected sale, forecast sale, lead days sales
        :return:
        """
        #######################################################
        # Expected sales = sum(T2 forecast sales)             #
        # forecasted_stock = closing of last frame of T1      #
        # Lead Days Sales = sum(Forecast sales of T1)         #
        # Demand Quantity = Expected Sales - Forecast Sales   #
        # Demand never in negative                            #
        #######################################################

        confirm = self.action_confirm()
        if confirm:
            return confirm
        product_suggestion_obj = self.env['requisition.product.suggestion.ept']
        product_ids = self.requisition_process_line_ids.mapped('product_id')
        forecast_stock_dict = {}
        lead_days_sales_dict = {}
        demand_dict = {}
        instock_dict = {}
        expected_dict = {}
        opening_stock_dict = {}
        self.clear_incoming_data()
        self.remove_requisition_summary_line_ept()
        for config_line in self.configuration_line_ids:

            # <====== Prepare t1 data =====>
            t1_start_date = self.requisition_date
            t1_end_date = config_line.po_schedule_date

            # Prepare t1 dict from ICR framing function
            # t1_dict format:
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

            # Prepare demand dict {(product_id, warehouse_id): demand qty}
            demand_dict.update({product_id: round(sum([value.get('ads', 0.0) * value.get('days', 0.0) for frame, value in frame_number.items() if value.get('state') == 'out_stock']), 0) for product_id, frame_number in t2_dict.items()})

            # Prepare demand dict {(product_id, warehouse_id): demand qty}
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

    def update_requisition_process_lines(self, forecast_stock_dict, lead_days_sales_dict, expected_dict, opening_stock_dict, demand_dict, instock_dict):
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
            round(opening_stock_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0) if opening_stock_dict.get((line.product_id.id, line.warehouse_id.id), 0.0) > 0 else 0.0,
            round(demand_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0)
            if round(demand_dict.get((line.product_id.id, line.warehouse_id.id), 0.0), 0) > 0 and line.can_be_update else line.adjusted_requisition_qty if not line.can_be_update else 0.0
            ) for line in self.requisition_process_line_ids] or []).strip('[]')

        if vals:
            # Update data of requisition process line with multiple records, fields and field values in one shot
            self._cr.execute("""update requisition_process_line_ept as t set
                                state = c.state,
                                forecasted_stock = c.forecasted_stock,
                                qty_available_for_sale = c.qty_available_for_sale,
                                expected_sale = c.expected_sale,
                                requisition_instock_qty = c.requisition_instock_qty,
                                requisition_qty = c.requisition_qty,
                                opening_stock = c.opening_stock,
                                adjusted_requisition_qty = c.adjusted_requisition_qty
                            from (values
                                {} 
                            ) as c(column_id, state, forecasted_stock, qty_available_for_sale, expected_sale, requisition_instock_qty, requisition_qty, opening_stock, adjusted_requisition_qty) 
                            where c.column_id = t.id;""".format(vals))
            self._cr.commit()

        return True

    def update_move_data(self, t2_dict):
        """
        Set incoming moves in requisition_process_line_ids
        :param t2_dict: framing data
        :return:
        """
        # Find incoming products list
        products = [key[0] for key, value in t2_dict.items() for k, v in value.items() if v.get('is_incoming', False)]

        # Find incoming products warehouses
        warehouses = [key[1] for key, value in t2_dict.items() for k, v in value.items() if v.get('is_incoming', False)]



        if products and warehouses:
            product_ids = '(' + str(products).strip('[]') + ')'
            warehouse_ids = '(' + str(warehouses).strip('[]') + ')'

            # Insert new move data in requisition_process_line_ids
            query = """
                        INSERT INTO requisition_process_line_move_data
                        (move_id, schedule_date, quantity, warehouse_id, picking_id, product_id, requisition_process_line_id)
                        SELECT move_id,schedule_date, quantity, warehouse_id, picking_id, product_id, (select id from requisition_process_line_ept where product_id = t.product_id and warehouse_id = t.warehouse_id and requisition_process_id = {})
                        FROM 
                        (SELECT move_id AS move_id, incoming_date AS schedule_date, incoming AS quantity, warehouse_id AS warehouse_id,
                         picking_id AS picking_id, product_id AS product_id  FROM get_incoming_data_with_move 
                         WHERE product_id in {} and warehouse_id in {})t
                     """.format(self.id, product_ids, warehouse_ids)
            self._cr.execute(query)
            self._cr.commit()
        return True

    def action_draft(self):
        is_approval_by_authorised = self.get_default_approval_by_authorised()
        is_use_forecast_sale_for_requisition = self.default_is_use_forecast_sale_for_requisition()
        self._cr.execute(
            """DELETE FROM requisition_process_line_ept where requisition_process_id = %s""" % (
                self.id))
        self._cr.execute(
            """DELETE FROM requisition_summary_line_ept where requisition_process_id = %s""" % (
                self.id))
        self.write({'state': 'draft', 'is_approval_by_authorised': is_approval_by_authorised,
                    'is_use_forecast_sale_for_requisition': is_use_forecast_sale_for_requisition})
        return True

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_re_calculate(self):
        return self.action_calculate()

    def unlink(self):
        if 'done' in self.mapped('state'):
            raise Warning("You can not delete transaction, if it is in Done state !!")
        res = super(RequisitionProcess, self).unlink()
        return res

    def action_confirm(self):
        line_obj = self.env['requisition.process.line.ept']
        if self.filtered(lambda x: not x.product_ids):
            raise UserError(_("Please add some products!!!"))
        if self.filtered(lambda x: not x.configuration_line_ids):
            raise UserError(_("Please select  Warehouse!!!!"))
        not_seller_product = self.product_ids - self.product_ids.filtered(
            lambda p: p.seller_ids.filtered(
                lambda s: s.name.id in [self.partner_id.id] + self.partner_id.child_ids.ids))
        if not_seller_product:
            not_seller_product_codes = not_seller_product.mapped('default_code')
            raise UserError(_("Supplier %s is not in following products : \n %s" % (
            self.partner_id.name, "\n\t".join(not_seller_product_codes))))

        for config_line in self.mapped('configuration_line_ids'):
            pickings = self.get_pending_moves(config_line.warehouse_id)
            if pickings:
                msg = """You cannot confirm that process, because some pickings need to be rescheduled.!!! \n"""
                for picking_name in pickings:
                    msg += "Move => %s / Source Document => %s \n" % (picking_name.get('name'),
                                                                      picking_name.get(
                                                                          'origin') if picking_name.get(
                                                                          'origin', False) else "")
                raise UserError(_(msg))
        product_ids = self.product_ids
        # use_forecast_sale_for_requisition = self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.use_forecasted_sales_for_requisition')
        if self.is_use_forecast_sale_for_requisition:
            list_of_period_ids = []
            product_ids = self.product_ids
            product_ids_str = '(' + str(product_ids.ids or [0]).strip('[]') + ')'
            total_time = 0
            warehouse_ids = self.mapped('configuration_line_ids').mapped('warehouse_id').ids
            for config_line in self.mapped('configuration_line_ids'):
                # warehouse_id = config_line.warehouse_id
                # warehouse_ids.append(warehouse_id.id)
                total_time = config_line.requisition_estimated_delivery_time + config_line.requisition_backup_stock_days
                # total = datetime.datetime.strptime(str(self.requisition_date), '%Y-%m-%d').date() + timedelta(days=int(total_time))
                total = self.requisition_date + timedelta(days=int(total_time))
                list_of_period_ids + self.env['requisition.period.ept'].search(
                    [('date_start', '<=', total), ('date_stop', '>=', self.requisition_date)]).ids

            period_ids_str = '(' + str(list(dict.fromkeys(list_of_period_ids)) or [0]).strip('[]') + ')'
            warehouse_ids_str = '(' + str(warehouse_ids or [0]).strip('[]') + ')'
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
                        
                """ % (
            str(product_ids_str), str(warehouse_ids_str), str(period_ids_str), str(product_ids_str),
            str(warehouse_ids_str), str(period_ids_str))

            self._cr.execute(not_found_query)
            res_dict = self._cr.dictfetchall()
            # for record in res_dict:
            #     not_found_lines.append((0, 0, record))
            not_found_lines = [(0, 0, res) for res in res_dict]

            if not_found_lines:
                vals = {
                    'requisition_process_id': self.id,
                    'mismatch_lines': not_found_lines,
                    'warehouse_ids': [(6, 0, warehouse_ids)]
                }
                context = vals.copy()
                mismatch = self.env['mismatch.data.ept'].with_context(context).create(vals)
                if mismatch:
                    return mismatch.wizard_view()
        vals_list = []
        for product in product_ids:
            for config_line in self.configuration_line_ids:
                existing_line = self.reqisition_line_can_be_created(product, config_line)
                #                     existing_line = line_obj.search([('requisition_process_id', '=', config_line.requisition_process_id.id,),
                #                                      ('configuraiton_line_id', '=', config_line.id),
                #                                      ('product_id', '=', product.id),
                #                                      ('warehouse_id', '=', config_line.warehouse_id.id),
                #                                      ])
                if existing_line:
                    vals_list.append({'requisition_process_id': config_line.requisition_process_id.id,
                            'configuraiton_line_id': config_line.id,
                            'product_id': product.id,
                            'warehouse_id': config_line.warehouse_id.id,
                            })
        if vals_list:
            line_obj.create(vals_list)
            self._cr.commit()

    def reqisition_line_can_be_created(self, product_id, configuraiton_line_id):
        reqistion_process_line_obj = self.env['requisition.process.line.ept']
        if self.deliver_to == 'general':
            requsition_process_line_id = reqistion_process_line_obj.search(
                [('product_id', '=', product_id.id),
                 ('configuraiton_line_id', '=', configuraiton_line_id.id),
                 ('requisition_process_id', '=', configuraiton_line_id.requisition_process_id.id),
                 ('warehouse_id', '=', configuraiton_line_id.warehouse_id.id)])
            if requsition_process_line_id:
                return False
            else:
                return True

    def print_requisition_process(self):
        return self.env.ref(
            'advance_purchase_ordering_ept.action_report_requisition_process_line_ept').report_action(
            self)

    def get_pending_moves(self, warehouse, product_ids=[]):
        product_ids = product_ids and product_ids or self.product_ids and self.product_ids.ids or []
        product_ids = '(' + str(product_ids or [0]).strip('[]') + ')'
        self._cr.execute("""select sp.name as name, sm.origin as origin from stock_move sm 
                            JOIN stock_location ld ON ld.id = sm.location_dest_id
                            JOIN stock_warehouse whd ON ld.parent_path::text ~~ concat('%s', whd.view_location_id, '%s')
                            JOIN stock_picking sp ON sp.id = sm.picking_id
                            where ld.usage = 'internal' and sm.date_expected::date < now()::date and sm.state = 'assigned' 
                            and sm.product_id in %s and sm.warehouse_id = %s order by sm.date_expected""" % ('%/', '/%', product_ids, warehouse.id))
        picking_names = self._cr.dictfetchall()
        return picking_names

    def action_approve(self):
        self.requisition_process_line_ids.write({'state': 'approved'})
        self.write({'state': 'approved'})
        return True

    def action_verify(self):
        self.write({'state': 'verified'})
        return True

    def action_requisition_email_sent(self, template_id):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env['mail.template'].browse(template_id)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='requisition.process.ept',
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
        if mark_rejected:
            ctx.update({'mark_requisition_as_rejected': mark_rejected,
                        'reject_reason': self._context.get('reject_reason', '')})

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

    def action_request_for_approval(self):
        self.ensure_one()
        approval_by_authorised = self.is_approval_by_authorised
        send_email = eval(self.env['ir.config_parameter'].sudo().get_param(
            'advance_purchase_ordering_ept.requisition_send_email'))
        approve_email_template_id = self.env.ref(
            'advance_purchase_ordering_ept.mail_template_reqisition_approve_ept').id
        action = {}
        if approval_by_authorised and send_email:
            if not approve_email_template_id:
                raise UserError(_("Email Template for Request For Approval not Found !!!"))
            if not self.approval_user_id:
                raise UserError(_("Please set Authorised User For Reorder Process !!!."))
            action = self.with_context(
                mark_requisition_as_waiting=True).action_requisition_email_sent(
                approve_email_template_id)
        else:
            self.write({'state': 'waiting'})
        return action

    def action_reject(self):
        ctx = self._context.copy()
        action = {
            'name': _('Reorder Reject Reason'),
            'view_mode': 'form',
            'res_model': 'requisition.reject.reason.ept',
            'view_id': self.env.ref(
                'advance_purchase_ordering_ept.requisition_reject_reason_ept_form_view').id,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'target': 'new'
        }
        return action

    def reject_requisition_with_reason(self, reason):
        approval_by_authorised = self.is_approval_by_authorised
        send_email = eval(self.env['ir.config_parameter'].sudo().get_param(
            'advance_purchase_ordering_ept.requisition_send_email'))
        reject_email_template_id = self.env.ref(
            'advance_purchase_ordering_ept.mail_template_reqisition_reject_ept').id
        action = {}
        if approval_by_authorised and send_email:
            if not reject_email_template_id:
                raise (_("Email Template for Reject not Found !!!"))
            action = self.with_context(mark_requisition_as_rejected=True,
                                       reject_reason=reason).action_requisition_email_sent(
                reject_email_template_id)
        else:
            self.write({'state': 'rejected', 'reject_reason': reason})
        return action

    def action_update_requisition(self):
        self.write({'state': 'generated'})
        return True

    def prepare_po_vals(self, requisition_configuration_line):
        self.ensure_one()
        warehouse = requisition_configuration_line.get_warehouse_for_purchase_order()
        purchase_obj = self.env['purchase.order'].with_context(
            force_company=warehouse.company_id.id)
        picking_type = warehouse and warehouse.in_type_id

        new_record = purchase_obj.new(
            {'partner_id': self.partner_id.id, 'picking_type_id': picking_type.id,
             'origin': self.name,
             'date_order': str(requisition_configuration_line.po_schedule_date),
             })
        new_record.company_id = warehouse.company_id
        new_record.onchange_partner_id()
        new_record.currency_id = requisition_configuration_line.purchase_currency_id
        new_record._compute_tax_id()
        new_record.picking_type_id = picking_type
        new_record._onchange_picking_type_id()
        vals = new_record._convert_to_write(new_record._cache)
        return vals

    def prepare_po_line_vals(self, purchase_order, product, ordered_qty):
        self.ensure_one()
        purchase_order_line_obj = self.env['purchase.order.line'].with_context(
            force_company=purchase_order.company_id and purchase_order.company_id.id or self._uid.company_id.id,
            from_requisition_process=True)

        order_line_data = {'product_id': product.id,
                           'order_id': purchase_order.id,
                           'product_qty': ordered_qty,
                           }
        po_line = purchase_order_line_obj.new(order_line_data)
        po_line.onchange_product_id()
        po_line.product_qty = ordered_qty
        po_line._onchange_quantity()
        po_vals = po_line._convert_to_write(po_line._cache)
        price_unit, uom_qty = self.get_purchase_product_price(purchase_order, product, po_line,
                                                              ordered_qty)
        po_vals.update({'price_unit': price_unit, 'product_qty': uom_qty})
        return po_vals

    def get_purchase_product_price(self, purchase_order, product, po_line, ordered_qty):
        price_unit = 0.0
        suppiler_info_obj = self.env['product.supplierinfo']
        partner_id = purchase_order.partner_id
        # supplier_id = partner_id and partner_id.id or False

        uom_qty = ordered_qty
        if partner_id:
            supplierinfo = suppiler_info_obj.search(
                [('name', '=', partner_id.id), ('product_id', '=', product.id)],
                limit=1)

        if not supplierinfo:
            supplierinfo = self.env['product.supplierinfo'].search(
                [('name', 'child_of', partner_id.id), ('product_id', '=', product.id)], limit=1)

        if not supplierinfo:
            supplierinfo = self.env['product.supplierinfo'].search(
                ['|', ('name', '=', partner_id.id), ('name', 'child_of', partner_id.id),
                 ('product_id', '=', False),
                 ('product_tmpl_id', '=', product and product.product_tmpl_id.id)], limit=1)

        if supplierinfo:
            company_id = self.company_id.id or purchase_order.company_id.id or self.env.user.company_id.id
            price_unit = self.env['account.tax']._fix_tax_included_price(supplierinfo.price,
                                                                         product.supplier_taxes_id.filtered(
                                                                             lambda
                                                                                 r: r.company_id.id == company_id),
                                                                         po_line.taxes_id) if supplierinfo else 0.0

            if price_unit and purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

            #         if seller and product.uom_id and seller.product_uom != product.uom_id:
            #             price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit,
            #                                                                 to_uom_id=product.uom_id.id)

            if product.uom_id and supplierinfo.product_uom != product.uom_id:
                # price_unit=seller.product_uom._compute_price(price_unit,product.uom_id)
                uom_qty = product.uom_id._compute_quantity(ordered_qty, supplierinfo.product_uom)
        else:
            return 0.0, 0.0
        return price_unit, uom_qty

    def action_done(self):
        """
        Create purchase order as per demand in summary
        :return:
        """
        self.ensure_one()
        purchase_order_obj = self.env['purchase.order']

        dest_warehouse_wise_po = {}
        po_wise_product_qty = {}
        for summary in self.requisition_summary_ids:
            for line in summary.requisition_process_line_ids.filtered(lambda x: x.adjusted_requisition_qty > 0):
                product = summary.product_id
                dest_warehouse_id = line.configuraiton_line_id.destination_warehouse_id.id
                po_qty = round(summary.po_qty * line.sharing_percent / 100, 0)
                purchase_order = dest_warehouse_wise_po.get(dest_warehouse_id)

                if not purchase_order:
                    po_vals = self.prepare_po_vals(line.configuraiton_line_id)
                    purchase_order = purchase_order_obj.create(po_vals)
                    dest_warehouse_wise_po.update({dest_warehouse_id: purchase_order})

                line.configuraiton_line_id.write({'purchase_order_id': purchase_order.id})
                if po_wise_product_qty.get(purchase_order):
                    if product in po_wise_product_qty[purchase_order]:
                        po_wise_product_qty[purchase_order][product] += po_qty
                    else:
                        po_wise_product_qty[purchase_order].update({product: po_qty})
                    # po_wise_product_qty[purchase_order][product] += po_qty if product in po_wise_product_qty[purchase_order] else po_wise_product_qty[purchase_order].update({product: po_qty})
                else:
                    po_wise_product_qty.update({purchase_order: {product: po_qty}})
        for po in po_wise_product_qty:
            lines = []
            for product in po_wise_product_qty[po]:
                line_vals = self.prepare_po_line_vals(po, product, po_wise_product_qty[po][product])
                lines.append((0, 0, line_vals))
            po_vals = {'requisition_process_id': self.id, 'order_line': lines}
            po.write(po_vals)
        self.write({'state': 'done'})
        return True

    def action_view_purchase_orders(self):
        self.ensure_one()
        tree_view_id = self.env.ref('purchase.purchase_order_tree').id
        form_view_id = self.env.ref('purchase.purchase_order_form').id
        purchase_order_ids = self.purchase_order_ids and self.purchase_order_ids.ids or []

        action = {'name': 'Purchase Order',
                  'type': 'ir.actions.act_window',
                  'res_model': 'purchase.order',
                  'target': 'current',
                  'context': self._context}

        if len(purchase_order_ids) == 1:
            action.update(
                {'view_id': form_view_id, 'res_id': purchase_order_ids[0], 'view_mode': 'form'})
        else:
            action.update({'view_id': False, 'view_mode': 'tree,form',
                           'views': [(tree_view_id, 'tree'), (form_view_id, 'form'), ],
                           'domain': "[('id','in',%s)]" % (purchase_order_ids)})
        return action
