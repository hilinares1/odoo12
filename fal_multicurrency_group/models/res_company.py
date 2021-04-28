# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = "res.company"
    # merge from multicurrency_ext
    _rec_name = "code"

    code = fields.Char('Code', Size="7", required=True, default=id)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]

    @api.model
    def _get_default_group_currency(self):
        for company in self:
            return company and company.parent_id and company.parent_id.currency_id and company.parent_id.currency_id.id or False

    group_currency_id = fields.Many2one(
        'res.currency',
        default=_get_default_group_currency,
        string="IFRS Currency")
