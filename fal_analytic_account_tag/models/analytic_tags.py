import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags'   
    )

    @api.multi
    def apply_to_line(self):
        for lines in self.invoice_line_ids:
            res = lines.analytic_tag_ids.ids + self.fal_analytic_tag_ids.ids
            result = list(set(res))
            lines.analytic_tag_ids = [(6, 0, result)]


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    fal_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account' 
    )
    fal_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags'
    )

    @api.multi
    def apply_to_line(self):
        for lines in self.line_ids:
            lines.analytic_account_id = self.fal_analytic_account_id.id

    @api.multi
    def apply_to_line_tag(self):
        for lines in self.line_ids:
            res = lines.analytic_tag_ids.ids + self.fal_analytic_tag_ids.ids
            result = list(set(res))
            lines.analytic_tag_ids = [(6, 0, result)]


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')


class AccountMove(models.Model):
    _inherit = 'account.move'

    fal_analytic_tag_ids = fields.Many2many(
        'account.analytic.tag',
        string='Analytic Tags'
    )

    @api.multi
    def apply_to_line(self):
        for lines in self.line_ids:
            res = lines.analytic_tag_ids.ids + self.fal_analytic_tag_ids.ids
            result = list(set(res))
            lines.analytic_tag_ids = [(6, 0, result)]
