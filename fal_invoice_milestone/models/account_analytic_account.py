from odoo import fields, models


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Term')
