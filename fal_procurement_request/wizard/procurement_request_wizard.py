# -*- coding: utf-8 -*-
from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class ProcurementRequestWizard(models.TransientModel):
    _name = "procurement.request.wizard"
    _description = "Procurement Request Wizard"

    def _get_product(self):
        context = dict(self.env.context)
        active_id = context.get('active_id', False)
        model = context.get('active_model')
        product_obj = self.env[model]
        if model == 'product.template':
            return product_obj.browse(active_id).product_variant_id.id
        else:
            return active_id

    fal_product_id = fields.Many2one(
        'product.product', string='Product', required=True,
        default=_get_product)
    fal_product_qty = fields.Float(
        string='Quantity', digits=dp.get_precision('Product Unit of Measure'),
        default=lambda *args: 1.0)
    fal_date_order = fields.Date(
        string='Order Date', required=True,
        default=lambda self: self._context.get(
            'date', fields.Date.context_today(self)))
    partner_id = fields.Many2one(
        'res.partner', string='Supplier', required=True,
        default=lambda self: self._get_supplier())
    fal_date_planned = fields.Date('Expected Date')

    @api.model
    def _get_supplier(self):
        product_obj = self.env['product.product']
        res = self.env.ref("fal_procurement_request.supplier_to_be_defined")
        context = dict(self._context or {})
        if context.get('active_id', False):
            product_id = product_obj.browse(context.get('active_id', False))
            if product_id.seller_ids:
                res = [product_id.seller_ids[0].name.id]
        return res and res[0] or False

    @api.multi
    def make_procurement_request(self):
        data_wizard = self 
        fal_date_order_v12 = data_wizard.fal_date_order.strftime('%Y-%m-%d') + ' 00:00:00'
        purchase_order_obj = self.env['purchase.order']
        company_id = self.env.user.company_id.id
        currency_id = self.env.user.company_id.currency_id.id
        req = purchase_order_obj.create({
            'fal_req_product_id': data_wizard.fal_product_id.id,
            'fal_req_product_description': data_wizard.fal_product_id.name,
            'fal_req_uom_id': data_wizard.fal_product_id.uom_po_id.id,
            'fal_req_product_qty': data_wizard.fal_product_qty,
            'date_order': fal_date_order_v12,
            'partner_id': data_wizard.partner_id.id,
            'origin': 'Direct from Product',
            'fal_req_user_id': self.env.user.id,
            'date_planned': data_wizard.fal_date_planned,
            'company_id': company_id,
            'currency_id': currency_id,
            'state': 'procurement_request'
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Procurement Request',
            'res_model': 'purchase.order',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env['ir.model.data'].get_object_reference(
                'fal_procurement_request', 'fal_procurement_request_tree')[1],
            'target': 'current',
            'nodestroy': False,
            'domain': '[("state","=","procurement_request")]',
        }

# End of ProcurementRequestWizard()
