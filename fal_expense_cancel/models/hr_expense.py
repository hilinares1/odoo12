from odoo import api, models


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.multi
    def expense_cancelled(self):
        moves = self.env['account.move']
        for expense in self:
            if expense.account_move_id:
                moves += expense.account_move_id
            #unreconcile all journal items of the expense, since the cancellation will unlink them anyway
            expense.account_move_id.line_ids.filtered(lambda x: x.account_id.reconcile).remove_move_reconcile()

        # First, set the expense as cancelled and detach the move ids
        self.write({'state': 'cancel', 'account_move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this expense was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        return True
