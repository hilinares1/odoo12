# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class propose_wizard(models.TransientModel):
    _name = "fal.partner.qualified.wizard"
    _description = "Partner Qualified"

    fal_company_title = fields.Many2one(
        'res.partner.title', string="Company Title")
    fal_partner_tags = fields.Many2many(
        'res.partner.category', string="Partner Tags")
    fal_number_employee = fields.Integer(string="Number Of Employee")
    fal_year_founded = fields.Selection([
        (yr, str(yr)) for yr in reversed(
            range(1800, (datetime.now().year) + 1)
        )], string="Year Founded")
    is_company = fields.Boolean()

    @api.multi
    def qualified(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        partner = self.env['res.partner'].browse(active_id)
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
