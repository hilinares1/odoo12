# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fal_title = fields.Char("Title")
    fal_attachment = fields.Binary(
        string='Supplier Quotation Attachment', filestore=True)
    fal_attachment_name = fields.Char(string='Attachment name')
    fal_partner_contact_person_id = fields.Many2one(
        'res.partner',
        'Contact Person'
    )

    #add by murha 12-02-2019
    fal_user_id = fields.Many2one(
        'res.users',   
        'Purchase Person',
        select=True,
        track_visibility='onchange'
    )
    # finish in here

    # sale archive
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide\
        the Sale Order without removing it.")

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).\
            onchange_partner_id()
        partner = self.partner_id
        self.fal_partner_contact_person_id = partner.child_ids and \
            partner.child_ids[0].id or False
        return res

    @api.multi
    def action_view_invoice(self):
        res = super(PurchaseOrder, self).action_view_invoice()
        res['fal_title'] = self.fal_title
        return res

    @api.one
    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        res = super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
        # return res[0], because every make a super on this function, always return a list.
        res[0]['fal_title'] = self.fal_title
        return res[0]

#edited by SANDI 04-03-2019
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    price_subtotal_vat = fields.Monetary(
        string='Subtotal with VAT',
        compute='_amount_line_vat',
        store=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(
            PurchaseOrderLine, self).onchange_product_id()
        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        internal_ref = product_lang.default_code\
            and '[%s]' % product_lang.default_code or ''
        '''
        At least, by default, (below)
        we should have the <name> (if other fields are empty).
        '''
        self.name = '%s %s' % (internal_ref, product_lang.name or '')
        # The concatenation [Internal Ref][Vendor ref] is ok (below)
        if product_lang.code:
            if ('[%s]' % product_lang.code) != internal_ref:
                self.name = '%s %s' % (internal_ref, '[%s]' % product_lang.code)
            if product_lang.description_purchase:
                self.name += '\n' + product_lang.description_purchase
                if product_lang.fal_supplier_info_product_name:
                    self.name += '\n' + product_lang.fal_supplier_info_product_name or ''
            elif product_lang.description_sale:
                self.name += '\n' + product_lang.description_sale
                if product_lang.fal_supplier_info_product_name:
                    self.name += '\n' + product_lang.fal_supplier_info_product_name or ''
        return res

    @api.multi
    @api.depends('price_unit', 'product_qty', 'taxes_id', 'discount')
    def _amount_line_vat(self):
        for line in self:
            if line.name:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.taxes_id.compute_all(
                    price,
                    line.order_id.currency_id,
                    line.product_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_id)
                line.price_subtotal_vat = taxes['total_included']
            else:
                line.price_subtotal_vat = 0
