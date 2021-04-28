# -*- coding: utf-8 -*-
from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        if res.partner_id and not res.has_group('base.group_portal'):
            res.partner_id.write({
                'parent_id': res.company_id.partner_id.id,
                'customer': False})
        return res
