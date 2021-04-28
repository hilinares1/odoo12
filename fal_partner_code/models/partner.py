# -*- coding:utf-8 -*-
from odoo import models, api


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, vals):
        if not vals.get('ref', False):
            if vals.get('is_company', False):
                if vals.get('customer', False) and vals.get('supplier', False):
                    vals['ref'] = self.env[
                        'ir.sequence'
                    ].next_by_code('sc.code.fwa') or '/'
                elif vals.get('customer', False):
                    vals['ref'] = self.env[
                        'ir.sequence'
                    ].next_by_code('customer.code.fwa') or '/'
                elif vals.get('supplier', False):
                    vals['ref'] = self.env[
                        'ir.sequence'
                    ].next_by_code('supplier.code.fwa') or '/'
                else:
                    vals['ref'] = self.env[
                        'ir.sequence'
                    ].next_by_code('n.code.fwa') or '/'
        return super(Partner, self).create(vals)
