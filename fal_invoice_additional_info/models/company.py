from odoo import fields, models, api


class CompanyLatePayment(models.Model):
    _inherit = 'res.company'

    fal_company_late_payment_statement = fields.Boolean('Late Payment Statement')
