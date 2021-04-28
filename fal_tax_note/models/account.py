from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    fal_is_tax_journal = fields.Boolean(string="Is Tax Journal")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fal_reported = fields.Boolean(string='Reported')
