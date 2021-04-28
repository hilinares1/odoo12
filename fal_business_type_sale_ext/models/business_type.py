from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BusinessType(models.Model):
    _inherit = 'fal.business.type'


    sale_sequence_ids = fields.Many2many('ir.sequence', 'clu_business_sale_seq_rel', 
        'business_type_id', 'seq_id', string='Sale Sequences', copy=False, 
        ondelete='cascade'
    )

    @api.multi
    def generate_sale_sequence(self):
        this_company_seq = self.crm_sequence_ids.filtered(lambda s: (s.company_id.id == self._context.get('company_id')))
        if not this_company_seq:
            sequence_env = self.env['ir.sequence']
            generated_sequence = sequence_env.create({
                'code': ''.join(['clu.sale.order.', str(self.id)]),
                'name': ''.join(['Cluedoo sale order ',self.name]),
                'prefix':self.fal_business_prefix,
                'suffix':self.fal_business_suffix,
                'number_increment':1,
                'implementation':'standard',
                'padding':3})
            self.sale_sequence_ids = [(4, generated_sequence.id)]
            return generated_sequence
        else:
            return this_company_seq

    @api.onchange('fal_business_prefix')
    def onchange_fal_business_prefix(self):
        res = super(BusinessType, self).onchange_fal_business_prefix()
        for sequence in self.sale_sequence_ids:
            sequence.write({'prefix': self.fal_business_prefix})

    @api.onchange('fal_business_suffix')
    def onchange_fal_business_suffix(self):
        res = super(BusinessType, self).onchange_fal_business_suffix()
        for sequence in self.sale_sequence_ids:
            sequence.write({'suffix': self.fal_business_suffix})
