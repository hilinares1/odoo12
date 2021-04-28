from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    def _get_fields(self):
        return self.env['fal.dynamic.mandatory.fields'].search([])

    fal_mandatory_fields = fields.Many2many(
        'fal.dynamic.mandatory.fields', string="Mandatory Qualification Fields", default=_get_fields,
        help="Choose fields to show when qualify the partner")


class Fieldtoshow(models.Model):
    _name = 'fal.dynamic.mandatory.fields'
    _description = 'Dynamic Mandatory Fields'

    name = fields.Char(string="Name")
