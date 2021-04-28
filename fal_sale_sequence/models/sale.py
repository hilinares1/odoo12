from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_number = fields.Char(
        'Quotation Number', size=64,
        readonly=True, index=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('fal.sale.quotation.number') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('fal.sale.quotation.number') or 'New'
        res = super(SaleOrder, self).create(vals)
        res.write({'quotation_number': vals['name']})
        return res

    @api.multi
    def action_confirm(self, ):
        for sale_id in self:
            order_number = self.env['ir.sequence'].with_context(force_company=self.company_id.id).next_by_code('sale.order') or _('New')
            # order_number = 'New'
            sale_id.write({
                'name': order_number,
                'quotation_number': sale_id.name
            })
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default['quotation_number'] = False
        return super(SaleOrder, self).copy(default)

    @api.one
    def _prepare_purchase_order_data(self, company, company_partner):
        """ Generate purchase order values, from the SO (self)
            :param company_partner : the partner representing the company of the SO
            :rtype company_partner : res.partner record
            :param company : the company in which the PO line will be created
            :rtype company : res.company record
        """
        # find location and warehouse, pick warehouse from company object
        PurchaseOrder = self.env['purchase.order']
        warehouse = company.warehouse_id and company.warehouse_id.company_id.id == company.id and company.warehouse_id or False
        if not warehouse:
            raise Warning(_('Configure correct warehouse for company(%s) from Menu: Settings/Users/Companies' % (company.name)))

        picking_type_id = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'), ('warehouse_id', '=', warehouse.id)
        ], limit=1)
        if not picking_type_id:
            intercompany_uid = company.intercompany_user_id.id
            picking_type_id = PurchaseOrder.sudo(intercompany_uid)._default_picking_type()
        res = {
            'name': self.env['ir.sequence'].sudo().next_by_code('fal.purchase.quotation.number'),
            'origin': self.name,
            'partner_id': company_partner.id,
            'picking_type_id': picking_type_id.id,
            'date_order': self.date_order,
            'company_id': company.id,
            'fiscal_position_id': company_partner.property_account_position_id.id,
            'payment_term_id': company_partner.property_supplier_payment_term_id.id,
            'auto_generated': True,
            'auto_sale_order_id': self.id,
            'partner_ref': self.name,
            'currency_id': self.currency_id.id
        }
        return res
