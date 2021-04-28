# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class ResPartner(models.Model):
    _inherit = "res.partner"

    fal_parent_company = fields.Many2one(
        'res.partner',
        string='Parent Company'
    )

    @api.constrains('fal_parent_company')
    def _check_parent_company_id(self):
        if not self._check_recursion(parent='fal_parent_company'):
            raise ValidationError(_('You cannot create a recursive Parent Company.'))

# End of ResPartner()
