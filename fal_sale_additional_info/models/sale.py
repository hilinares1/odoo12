# -*- coding: utf-8 -*-

from odoo import models, fields, api
import openerp.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_title = fields.Char("Title")
    fal_attachment = fields.Binary(
        string='Customer PO Attachment', filestore=True)
    fal_attachment_name = fields.Char(string='Attachment name')
    fal_partner_contact_person_id = fields.Many2one(
        'res.partner',
        'Contact Person'
    )

    # sale archive
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide\
        the Sale Order without removing it.")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(SaleOrder, self).\
            onchange_partner_id()
        partner = self.partner_id
        self.fal_partner_contact_person_id = partner.child_ids and \
            partner.child_ids[0].id or False
        return res

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['fal_title'] = self.fal_title
        return res

    @api.one
    def _prepare_purchase_order_data(self, company, company_partner):
        res = super(SaleOrder, self)._prepare_purchase_order_data(company, company_partner)
        for item in res:
            item['fal_title'] = self.fal_title
        return res

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    #edited by sandi 04-03-2019 --> change float to monetary
    price_subtotal_vat = fields.Monetary(string='Subtotal with VAT', compute='_amount_line_vat', store=True)

    @api.multi
    @api.depends('price_unit', 'product_uom_qty', 'tax_id', 'discount', 'order_id')
    def _amount_line_vat(self):
        for line in self:
            if line.name:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, line.product_id, line.order_id.partner_id)
                line.price_subtotal_vat = taxes['total_included']
            else:
                line.price_subtotal_vat = 0
