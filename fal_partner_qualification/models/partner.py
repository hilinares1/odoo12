# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class Partner(models.Model):
    _inherit = 'res.partner'

    state = fields.Selection(
        [
            ('to_qualify', 'To Qualify'),
            ('unqualified', 'Unqualified'),
            ('qualified', 'Qualified')
        ],
        'Qualification State', required=True,
        default='to_qualify', readonly=1,
        track_visibility='onchange'
    )
    # move readonly to xml
    # keep this field, to keep data that already used this field.
    name = fields.Char()
    # ======================
    user_id = fields.Many2one(
        readonly=True, states={
            'unqualified': [('readonly', False)],
            'to_qualify': [('readonly', False)]})
    parent_id = fields.Many2one(
        readonly=True, states={
            'unqualified': [('readonly', False)],
            'to_qualify': [('readonly', False)]})
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
    def action_set_to_qualified(self):
        if self.is_company:
            context = {
                'default_is_company': True,
                'default_fal_company_title': self.fal_company_title.id,
                'default_fal_partner_tags': [
                    (6, 0, self.fal_partner_tags.ids)],
                'default_fal_number_employee': self.fal_number_employee,
                'default_fal_year_founded': self.fal_year_founded,
            }
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'fal.partner.qualified.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
            }
        else:
            parent = self.parent_id
            if parent:
                if parent.state == 'qualified':
                    self.state = 'qualified'
                elif parent.state == 'unqualified':
                    raise ValidationError(_('You cannot make this qualification for this contact, \
                        because the company of this contact \
                        is not Qualified --> \
                        please do the qualification for the company'))
                else:
                    raise ValidationError(_(
                        'The company of this contact need to be Qualified, \
                        --> please do the qualification for the company'))
            else:
                context = {
                    'default_fal_partner_tags': [
                        (6, 0, self.fal_partner_tags.ids)],
                }
                return {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'fal.partner.qualified.wizard',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'context': context,
                }

    @api.multi
    def action_set_to_unqualified(self):
        self.state = 'unqualified'
        if self.is_company:
            # Also make all child_ids as qualified
            for child_id in self.child_ids:
                child_id.state = 'unqualified'


# Additional Field and object form module fal_res_partner_ext

class ResPartner(models.Model):
    _inherit = 'res.partner'

    fal_department_id = fields.Many2one('hr.department', 'Department')
    fal_function_id = fields.Many2one('fal.function', 'Function')
    fal_company_size_id = fields.Many2one('fal.company.size', 'Company Size')
    fal_origin_id = fields.Many2one('fal.origin', 'Origin')


class FalFunction(models.Model):
    _name = 'fal.function'
    _description = 'Function'

    name = fields.Char('Name', required=True, translate=True)


class FalCompanySize(models.Model):
    _name = 'fal.company.size'
    _description = 'Company Size'

    name = fields.Char('Name', required=True, translate=True)


class FalOrigin(models.Model):
    _name = 'fal.origin'
    _description = 'Origin'

    name = fields.Char('Name', required=True, translate=True)
