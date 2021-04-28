from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    fal_expected_payment_date = fields.Date(
        string='Expected payment date')

    @api.onchange('date_due')
    def _onchange_date_due(self):
        if self.date_due:
            self.fal_expected_payment_date = self.date_due

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for item in self:
            item.move_id.write({
                'fal_expected_payment_date': item.fal_expected_payment_date})
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountInvoice, self).write(vals)
        self.move_id.write({
            'fal_expected_payment_date': self.fal_expected_payment_date})
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    fal_expected_payment_date = fields.Date(string='Expected payment date')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    expected_pay_date = fields.Date(
        related='move_id.fal_expected_payment_date', store=True)

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if vals.get('expected_pay_date', False):
            self.move_id.write({
                'fal_expected_payment_date': self.expected_pay_date})
            self.invoice_id.write({
                'fal_expected_payment_date': self.expected_pay_date})
        return res
