from odoo import fields, models, api, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    fal_business_type = fields.Many2one("fal.business.type", string="Business Type")

    @api.model
    def create(self, vals):
        if vals.get('fal_business_type'):
            business_type_obj = self.env['fal.business.type'].browse(vals.get('fal_business_type'))
            sequence_obj = business_type_obj.with_context(company_id=vals['company_id']).generate_sale_sequence()
            if vals.get('name', _('New')) == _('New'):
                if 'company_id' in vals:
                    vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(sequence_obj.code) or _('New')
                else:
                    vals['name'] = self.env['ir.sequence'].next_by_code(sequence_obj.code) or _('New')
        return super(SaleOrder, self).create(vals)
