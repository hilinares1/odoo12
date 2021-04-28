# -*- coding: utf-8 -*-

# import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _get_supplier(self):
        res = self.env.ref("fal_procurement_request.supplier_to_be_defined")
        return res and res[0] or False

    state = fields.Selection(
        selection_add=[(
            'procurement_request',
            'Procurement Request')],
    )
    fal_req_product_id = fields.Many2one(
        'product.product',
        string='Procurement Product',
        domain=[('purchase_ok', '=', True)],
        change_default=True, copy=False)
    fal_req_product_description = fields.Text('Description', copy=False)
    fal_req_product_qty = fields.Float(
        string='Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=1.00, copy=False)
    fal_req_uom_id = fields.Many2one('uom.uom', string="UOM", copy=False)
    fal_warehouse_manager_comment = fields.Text(
        'Requirer Comment', copy=False)
    fal_req_user_id = fields.Many2one(
        'res.users', string="Request By",
        default=lambda self: self.env.user, copy=False)
    fal_request_no = fields.Char(string="Request No", copy=False)
    partner_id = fields.Many2one(
        default=lambda self: self._get_supplier(), copy=False)

    fal_incoterm_id = fields.Many2one('account.incoterms', string='Incoterm')
    sale_order_line_order_invoiceterm = fields.Char(compute='_get_sale_order_invoiceterm', string='Sale Order Invoice Term')
    sale_order_line_order_id = fields.Many2one('sale.order', string="Sale Order", readonly=True, copy=False)
    sale_order_line_order_currency = fields.Many2one('res.currency', related='sale_order_line_order_id.currency_id', string="Sale Order Currency", readonly=True)
    sale_order_line_order_paymentterm = fields.Many2one('account.payment.term', related='sale_order_line_order_id.payment_term_id', string="Sale Order Payment Term", readonly=True)

    @api.multi
    def _get_sale_order_invoiceterm(self):
        for order in self:
            val_order_policy = ''
            if order.sale_order_line_order_id is False:
                break
            elif order.sale_order_line_order_id.picking_policy == 'direct':
                val_order_policy = 'On Demand'
            elif order.sale_order_line_order_id.picking_policy == 'one':
                val_order_policy = 'On Delivery Order'
            else:
                val_order_policy = 'Before Delivery'
            order.sale_order_line_order_invoiceterm = val_order_policy

    @api.multi
    @api.onchange('fal_req_product_id')
    def onchange_req_product_id(self):
        req_product_id = self.fal_req_product_id
        if req_product_id:
            partner_id = self._get_supplier()
            partner = req_product_id.seller_ids
            if partner:
                partner_id = partner[0].name.id
            self.fal_req_product_description = req_product_id.name
            self.fal_req_uom_id = req_product_id.uom_po_id.id
            self.partner_id = partner_id

    @api.model
    def create(self, vals):
        if vals.get('fal_req_product_id', False):
            vals['fal_request_no'] = self.env[
                'ir.sequence'].next_by_code('request.no') or ''

            uom_obj = self.env['uom.uom']
            acc_pos_obj = self.env['account.fiscal.position']
            product_obj = self.env['product.product']
            partner_obj = self.env['res.partner']
            order_line_obj = self.env['purchase.order.line']
            currency_obj = self.env['res.currency']
            company_obj = self.env['res.company']

            product_id = product_obj.browse(vals['fal_req_product_id'])
            partner_id = partner_obj.browse(vals['partner_id'])
            currency_id = currency_obj.browse(vals['currency_id'])
            company_id = company_obj.browse(vals['company_id'])

            if uom_obj.browse(vals.get('fal_req_uom_id', False)):
                qty = uom_obj.browse(vals.get(
                    'fal_req_uom_id', False
                ))._compute_quantity(vals.get(
                    'fal_req_product_qty', 0
                ), uom_obj.browse(vals.get(
                    'fal_req_uom_id', False) or product_id.uom_po_id.id))

            taxes_ids = product_id.supplier_taxes_id
            taxes = acc_pos_obj.map_tax(
                partner_id.property_account_position_id, taxes_ids)
            price = 0.00
            if partner_id:
                if product_id.seller_ids:
                    price = product_id.seller_ids[0].price
                    if currency_id and company_id and currency_id != product_id.seller_ids[0].currency_id:
                        price = product_id.seller_ids[0].currency_id._convert(
                            price, currency_id, company_id,
                            vals['date_order'] or fields.Date.today())

            supplierinfo = False
            for supplier in product_id.seller_ids:
                if partner_id and (supplier.name.id == partner_id.id):
                    supplierinfo = supplier

            if supplierinfo:
                dt = order_line_obj._get_date_planned(
                    supplierinfo).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            else:
                dt = datetime.strptime(
                    vals['date_order'], DEFAULT_SERVER_DATETIME_FORMAT
                ) + relativedelta(
                    days=product_id.sale_delay)
            vals['order_line'] = [(0, 0, {
                'product_id': product_id.id,
                'name': vals.get(
                    'fal_req_product_description', False) or product_id.name,
                'product_qty': vals.get('fal_req_product_qty', False) or vals.get('qty', False) or 0,
                'product_uom': vals.get(
                    'fal_req_uom_id', False) or product_id.uom_po_id.id,
                'price_unit': price,
                'date_planned': vals.get('date_planned', False) or dt,
                'taxes_id': [(6, 0, taxes)],
                'fal_req_user_id': vals.get('fal_req_user_id', False),
                'fal_request_no': vals.get('fal_request_no', False),
                'fal_request_qty': vals.get('fal_req_product_qty', False),
                'fal_warehouse_manager_comment': vals.get(
                    'fal_warehouse_manager_comment', False)}
            )]
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        for purchase_id in self:
            supplier = []
            price = 0.00
            partner = vals.get('partner_id', False)
            if partner:
                for sup in self.fal_req_product_id.seller_ids:
                    supplier.append(sup.name.id)
                    if partner in supplier:
                        supplierinfo = self.fal_req_product_id.seller_ids.filtered(lambda r: r.name.id == partner)
                        price = supplierinfo[0].price
                        if self.currency_id and self.company_id and self.currency_id != supplierinfo[0].currency_id:
                            price = supplierinfo[0].currency_id._convert(
                                price, self.currency_id, self.company_id,
                                self.date_order or fields.Date.today())

            for purchase_line_id in purchase_id.order_line.filtered(lambda r: r.fal_request_no):
                val = {
                    'name': purchase_line_id.name,
                    'product_qty': purchase_line_id.product_qty,
                    'fal_warehouse_manager_comment': purchase_line_id.fal_warehouse_manager_comment,
                    'product_uom': purchase_line_id.product_uom.id,
                    'fal_req_user_id': purchase_line_id.fal_req_user_id.id,
                    'fal_request_no': purchase_line_id.fal_request_no,
                    'fal_request_qty': purchase_line_id.fal_request_qty,
                    'price_unit': purchase_line_id.price_unit,
                }
                val_change = False
                if vals.get('partner_id', False):
                    val.update({'price_unit': price})
                    val_change = True
                if vals.get('fal_req_product_id', False):
                    val.update({'product_id': vals.get(
                        'fal_req_product_id', False)})
                    val_change = True
                if vals.get('fal_req_product_description', False):
                    val.update({'name': vals.get(
                        'fal_req_product_description', False)})
                if vals.get('fal_req_product_qty', 0):
                    val.update({
                        'product_qty': vals.get('fal_req_product_qty', 0),
                        'fal_request_qty': vals.get('fal_req_product_qty', 0)
                    })
                    val_change = True
                if vals.get('fal_warehouse_manager_comment', False):
                    val.update({'fal_warehouse_manager_comment': vals.get(
                        'fal_warehouse_manager_comment', False)})
                    val_change = True
                if vals.get('fal_req_uom_id', False):
                    val.update({'product_uom': vals.get(
                        'fal_req_uom_id', False)})
                    val_change = True
                if vals.get('fal_req_user_id', False):
                    val.update({'fal_req_user_id': vals.get(
                        'fal_req_user_id', False)})
                    val_change = True
                if val_change:
                    purchase_line_id.write(val)
        return super(PurchaseOrder, self).write(vals)

    # 3. Can't delete Procurement Request, as well as Draft Quotation
    @api.multi
    def unlink(self):
        for purchase_orders in self:
            if purchase_orders.state in ('draft', 'procurement_request'):
                purchase_orders.write({'state': 'cancel'})
        return super(PurchaseOrder, self).unlink()

    @api.multi
    def action_mark_rfq(self):
        return self.write({'state': 'draft'})

    @api.multi
    def button_confirm(self):
        # todo = []
        for po in self:
            if not po.order_line:
                raise UserError(_(
                    'Error! You cannot confirm a purchase order \
                    without any purchase order line.'))
            if po.partner_id == self.env.ref(
                    "fal_procurement_request.supplier_to_be_defined"):
                raise UserError(_(
                    'Invalid Action! In order to confirm a quotation, \
                    you must define supplier first.'))
        return super(PurchaseOrder, self).button_confirm()

# End of PurchaseOrder()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fal_warehouse_manager_comment = fields.Text(
        string='Requirer Comment', copy=False)
    fal_request_no = fields.Char(string="Request No", copy=False)
    fal_req_user_id = fields.Many2one(
        'res.users', string="Request By", copy=False)
    fal_request_qty = fields.Float(string="Request Qty", copy=False)

    # OLDNAME: _prepare_order_line_move
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for rex in res:
            rex[
                'fal_warehouse_manager_comment'
            ] = self.fal_warehouse_manager_comment
        return res

# End of PurchaseOrderLine()
