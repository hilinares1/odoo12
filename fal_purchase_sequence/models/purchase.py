from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'fal.purchase.quotation.number') or 'New'
        res = super(PurchaseOrder, self).create(vals)
        res.write({'quotation_number': vals['name']})
        return res

    @api.multi
    def button_confirm(self):
        for sale_id in self:
            order_number = self.env['ir.sequence'].\
                next_by_code('purchase.order') or 'New'
            sale_id.write({
                'name': order_number,
            })
        return super(PurchaseOrder, self).button_confirm()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['quotation_number'] = False
        return super(PurchaseOrder, self).copy(default)

    @api.one
    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):
        """ Generate the Sale Order values from the PO
            :param name : the origin client reference
            :rtype name : string
            :param partner : the partner reprenseting the company
            :rtype partner : res.partner record
            :param company : the company of the created SO
            :rtype company : res.company record
            :param direct_delivery_address : the address of the SO
            :rtype direct_delivery_address : res.partner record
        """
        partner_addr = partner.sudo().address_get(['invoice', 'delivery', 'contact'])
        warehouse = company.warehouse_id and company.warehouse_id.company_id.id == company.id and company.warehouse_id or False
        if not warehouse:
            raise Warning(_('Configure correct warehouse for company(%s) from Menu: Settings/Users/Companies' % (company.name)))
        return {
            'name': self.env['ir.sequence'].sudo().next_by_code('fal.sale.quotation.number') or '/',
            'company_id': company.id,
            'warehouse_id': warehouse.id,
            'client_order_ref': name,
            'partner_id': partner.id,
            'pricelist_id': partner.property_product_pricelist.id,
            'partner_invoice_id': partner_addr['invoice'],
            'date_order': self.date_order,
            'fiscal_position_id': partner.property_account_position_id.id,
            'user_id': False,
            'auto_generated': True,
            'auto_purchase_order_id': self.id,
            'partner_shipping_id': direct_delivery_address or partner_addr['delivery']
        }
