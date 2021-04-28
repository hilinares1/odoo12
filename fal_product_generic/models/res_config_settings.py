# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"

    fal_set_company_product_blank = fields.Boolean(
        string="Company Product Blank",
        help="if check it will set a company as blank, if not check it will set company to current company")


class FalResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_set_company_product_blank = fields.Boolean(
        string="Company Product Blank",
        related='company_id.fal_set_company_product_blank',
        readonly=False,
        help="if check it will set a company as blank, if not check it will set company to current company")

    @api.multi
    def execute(self):
        res = super(FalResConfigSettings, self).execute()
        company_id = self.env.user.company_id.id
        json_value = 0
        if self.fal_set_company_product_blank:
            default = self.env['ir.default'].search([
                ('field_id', '=', self.env.ref("product.field_product_product__company_id").id),
                ('company_id', '=', company_id),
            ])
            default_template = self.env['ir.default'].search([
                ('field_id', '=', self.env.ref("product.field_product_template__company_id").id),
                ('company_id', '=', company_id),
            ])
            if not default:
                self.env['ir.default'].create({
                    'field_id': self.env.ref("product.field_product_product__company_id").id,
                    'company_id': company_id,
                    'json_value': json_value,
                })
            if not default_template:
                self.env['ir.default'].create({
                    'field_id': self.env.ref("product.field_product_template__company_id").id,
                    'company_id': company_id,
                    'json_value': json_value,
                })
        else:
            domain = [
                ('field_id', 'in', [
                    self.env.ref("product.field_product_product__company_id").id,
                    self.env.ref("product.field_product_template__company_id").id]),
                ('company_id', '=', company_id)]
            self.env['ir.default'].search(domain).unlink()
        return res
