
# -*- coding: utf-8 -*-
from odoo import models, api, fields
from datetime import datetime


class sale_propose_wizard(models.TransientModel):
    _inherit = "fal.sale.proposal.wizard"

    is_qualified = fields.Selection(related="sale_order_id.partner_id.state")
    is_company = fields.Boolean(related="sale_order_id.partner_id.is_company")
    fal_company_title = fields.Many2one(
        'res.partner.title', string="Company Title")
    fal_partner_tags = fields.Many2many(
        'res.partner.category', 'res_partner_id',
        'res_partner_res_partner_category_rel',
        string="Partner Tags")
    fal_number_employee = fields.Integer(string="Number Of Employee")
    fal_year_founded = fields.Selection([
        (yr, str(yr)) for yr in reversed(
            range(1800, (datetime.now().year) + 1)
        )], string="Year Founded")

    @api.multi
    def partner_qualified_and_confirm(self):
        partner = self.sale_order_id.partner_id
        partner.write({
            'fal_partner_tags': [(6, 0, self.fal_partner_tags.ids)],
            'fal_number_employee': self.fal_number_employee,
            'fal_year_founded': self.fal_year_founded,
            'fal_company_title': self.fal_company_title.id,
            'state': 'qualified',
        })
        # Also make all child_ids as qualified
        for child_id in partner.child_ids:
            child_id.state = 'qualified'
        self.sale_order_id.action_propose()
