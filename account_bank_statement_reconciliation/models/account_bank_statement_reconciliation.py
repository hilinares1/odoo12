from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.depends('balance_end_real', 'balance_end')
    def _margin_compute(self):
        for statement in self:
            statement.margin_compute = statement.balance_end_real - statement.balance_end

    margin_compute = fields.Float(
        compute='_margin_compute',
        string='Computed Margin',
        readonly=True, store=True,
        help='Margin as calculated Ending balance minuse Computed Balance')

    def button_line_delete(self):
        for statement in self:
            if statement.move_line_ids:
                self.write({'move_line_ids': [(5, False, False)]})
            return True


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def button_cancel_reconciliation(self):
        for line in self:
            if line.statement_id.state == 'confirm':
                line.statement_id.write({'state': 'draft'})
        return super(AccountBankStatementLine, self).button_cancel_reconciliation()


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    @api.multi
    def cancel_voucher(self):
        for voucher in self:
            voucher.refresh()
            for line in voucher.move_id.line_ids:
                if line.statement_id.state == 'confirm':
                    raise UserError(_('Can\'t be unreconciled because the bank statement: "%s" is already closed, Please open the bank statement first!') % line.statement_id.name)
        return super(AccountVoucher, self).cancel_voucher()
