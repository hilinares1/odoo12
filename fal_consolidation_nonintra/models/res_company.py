# -*- coding: utf-8 -*-
from odoo import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        company = super(ResCompany, self).create(vals)
        # after creating new company
        # update non intra domain in IrFilter
        self.env['ir.filters'].update_non_intra_domain()
        return company

    @api.multi
    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        # if partner_id is changed
        if vals.get('partner_id'):
            # update non intra domain in IrFilter
            self.env['ir.filters'].update_non_intra_domain()
        return res

    @api.multi
    def unlink(self):
        res = super(ResCompany, self).unlink()
        # after company deletion, update non intra domain
        self.env['ir.filters'].update_non_intra_domain()
        return res
