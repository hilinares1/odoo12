# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    fal_set_company_payment_term_blank = fields.Boolean(
        string="Company Payment Term Blank",
        help="if check it will set a company as blank, if not check it will set company to current company")


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_set_company_payment_term_blank = fields.Boolean(
        string="Company Payment Term Blank",
        related='company_id.fal_set_company_payment_term_blank',
        help="if check it will set a company as blank, if not check it will set company to current company", readonly=False)

    @api.multi
    def execute(self):
        res = super(FalResConfigSettings, self).execute()
        company_id = self.env.user.company_id.id
        json_value = 0
        if self.fal_set_company_payment_term_blank:
            default = self.env['ir.default'].search([
                ('field_id', '=', self.env.ref("account.field_account_payment_term__company_id").id),  #
                ('company_id', '=', company_id),
            ])
            if not default:
                self.env['ir.default'].create({
                    'field_id': self.env.ref("account.field_account_payment_term__company_id").id,
                    'company_id': company_id,
                    'json_value': json_value,
                })
        else:
            domain = [('field_id', '=', self.env.ref("account.field_account_payment_term__company_id").id),
                      ('company_id', '=', company_id)]
            self.env['ir.default'].search(domain).unlink()
        return res
