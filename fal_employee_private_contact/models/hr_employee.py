# -*- coding: utf-8 -*-

from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        partner = self.env['res.partner']
        part = partner.create({
            'name': vals['name'],
            'type': 'private',
            'is_employee': True,
            'customer': False,
            'supplier': True,

        })
        vals['address_home_id'] = part.id
        return super(HrEmployee, self).create(vals)
