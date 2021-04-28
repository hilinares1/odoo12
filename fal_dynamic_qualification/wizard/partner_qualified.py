# -*- coding: utf-8 -*-
from odoo import models, fields, api


class propose_wizard(models.TransientModel):
    _inherit = "fal.partner.qualified.wizard"

    def _get_field_to_show(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        partner = self.env['res.partner'].browse(active_id)
        return partner.company_id.fal_mandatory_fields.ids

    email = fields.Char()
    phone = fields.Char()

    # fields to show
    fal_mandatory_fields = fields.Many2many(
        'fal.dynamic.mandatory.fields', default=_get_field_to_show)
    is_company_title = fields.Boolean(
        'is company title', compute="_check_feilds_to_show")
    is_partner_tags = fields.Boolean(
        'is partner tags', compute="_check_feilds_to_show")
    is_number_employee = fields.Boolean(
        'is number of employee', compute="_check_feilds_to_show")
    is_year_founded = fields.Boolean(
        'is year founded', compute="_check_feilds_to_show")
    is_email = fields.Char()
    is_phone = fields.Char()

    @api.depends('fal_mandatory_fields')
    def _check_feilds_to_show(self):
        context = dict(self._context)
        active_id = context.get('active_id')
        partner = self.env['res.partner'].browse(active_id)
        for item in self:
            if self.env.ref(
                'fal_dynamic_qualification.fal_company_title_fields'
            ) in item.fal_mandatory_fields and partner.company_type != 'person':
                item.is_company_title = True
            if self.env.ref(
                'fal_dynamic_qualification.fal_year_founded_fields'
            ) in item.fal_mandatory_fields and partner.company_type != 'person':
                item.is_year_founded = True
            if self.env.ref(
                'fal_dynamic_qualification.fal_number_employee_fields'
            ) in item.fal_mandatory_fields and partner.company_type != 'person':
                item.is_number_employee = True
            if self.env.ref(
                'fal_dynamic_qualification.fal_partner_tags_fields'
            ) in item.fal_mandatory_fields:
                item.is_partner_tags = True
            if self.env.ref(
                'fal_dynamic_qualification.fal_phone_fields'
            ) in item.fal_mandatory_fields:
                item.is_phone = True
            if self.env.ref(
                'fal_dynamic_qualification.fal_email_fields'
            ) in item.fal_mandatory_fields:
                item.is_email = True

    @api.multi
    def qualified(self):
        res = super(propose_wizard, self).qualified()
        context = dict(self._context)
        active_id = context.get('active_id')
        partner = self.env['res.partner'].browse(active_id)
        partner.write({
            'email': self.email,
            'phone': self.phone,
        })
        return res


# class sale_propose_wizard(models.TransientModel):
#     _inherit = "fal.sale.proposal.wizard"

#     email = fields.Char()
#     phone = fields.Char()

#     # fields to show
#     fal_mandatory_fields = fields.Many2many(
#         'fal.dynamic.mandatory.fields',
#         related="sale_order_id.partner_id.company_id.fal_mandatory_fields")
#     is_company_title = fields.Boolean(
#         'is company title', compute="_check_feilds_to_show")
#     is_partner_tags = fields.Boolean(
#         'is partner tags', compute="_check_feilds_to_show")
#     is_number_employee = fields.Boolean(
#         'is number of employee', compute="_check_feilds_to_show")
#     is_year_founded = fields.Boolean(
#         'is year founded', compute="_check_feilds_to_show")
#     is_email = fields.Char()
#     is_phone = fields.Char()

#     @api.depends('fal_mandatory_fields')
#     def _check_feilds_to_show(self):
#         for item in self:
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_company_title_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_company_title = True
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_year_founded_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_year_founded = True
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_number_employee_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_number_employee = True
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_partner_tags_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_partner_tags = True
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_phone_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_phone = True
#             if self.env.ref(
#                 'fal_dynamic_qualification.fal_email_fields'
#             ) in item.fal_mandatory_fields:
#                 item.is_email = True

#     @api.multi
#     def partner_qualified_and_confirm(self):
#         res = super(sale_propose_wizard, self).partner_qualified_and_confirm()
#         partner = self.sale_order_id.partner_id
#         partner.write({
#             'email': self.email,
#             'phone': self.phone,
#         })
#         return res
