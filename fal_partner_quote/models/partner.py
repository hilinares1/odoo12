from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ref = fields.Char(copy=False)

    @api.constrains('ref')
    def _check_ref(self):
        for partner in self:
            partners = partner.search([('ref', '=', partner.ref)])
            if partner and len(partners) > 1:
                msg = _('This Ref is already used by another partner.\
                    It should be "Last partner ID +1".\
                    Please manually input it and save')
                raise ValidationError(msg)

    # NEW SEQUENCE FOR INTERNAL REF
    @api.model
    def create(self, vals):
        if not vals.get('ref', False):
            vals['ref'] = self.env['ir.sequence'].\
                next_by_code('fal.internal.ref.sequence') or '/'
        return super(ResPartner, self).create(vals)
