from odoo import fields, models, api, _


class Lead(models.Model):
    _inherit = 'crm.lead'

    fal_seq_name = fields.Char(
        'Clu name', copy=False, readonly=True, default=_('New')
    )   
    fal_business_type = fields.Many2one("fal.business.type", string="Business Type")

    @api.model
    def create(self, vals):
        res = super(Lead, self).create(vals)
        if res.fal_business_type:
            sequence_obj = res.fal_business_type.with_context(company_id=vals['company_id']).generate_crm_sequence()
            if res.fal_seq_name == _('New'):
                res.fal_seq_name = self.env['ir.sequence'].next_by_code(sequence_obj.code) or _('New')
        return res
