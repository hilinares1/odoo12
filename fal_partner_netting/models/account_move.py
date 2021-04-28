from odoo import models, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _check_reconcile_validity(self):
        #Perform all checks on lines
        company_ids = set()
        all_accounts = []
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if len(set(all_accounts)) > 1:
            # raise UserError(_('Entries are not of the same account!'))
            # Change from here
            # Create account move
            journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
            if not journal:
                raise UserError(_('Journal not found. Please create a journal with type "Miscellaneous".'))
            move = self.env['account.move'].create({
                'ref': _('AR/AP netting'),
                'journal_id': journal.id,
            })
            # Group amounts by account
            account_groups = []
            for move_line in self:
                account_groups.append({
                    'id': move_line.id,
                    'account_id':move_line.account_id,
                    'debit': move_line.debit,
                    'credit':move_line.credit,
                })
            debtors = []
            creditors = []
            total_debtors = 0
            total_creditors = 0
            for account_group in account_groups:
                balance = account_group['debit'] - account_group['credit']
                group_vals = {
                    'account_id': account_group['account_id'][0],
                    'balance': abs(balance),
                }
                if balance > 0:
                    debtors.append(group_vals)
                    total_debtors += balance
                else:
                    creditors.append(group_vals)
                    total_creditors += abs(balance)
            # Create move lines
            netting_amount = min(total_creditors, total_debtors)
            field_map = {1: 'debit', 0: 'credit'}
            move_lines = []
            for i, group in enumerate([debtors, creditors]):
                available_amount = netting_amount
                for account_group in group:
                    if account_group['balance'] > available_amount:
                        amount = available_amount
                    else:
                        amount = account_group['balance']
                    move_line_vals = {
                        field_map[i]: amount,
                        'partner_id': line[0].partner_id.id,
                        'date': move.date,
                        'journal_id': move.journal_id.id,
                        'name': move.ref,
                        'account_id': account_group['account_id'].id,
                    }
                    move_lines.append((0, 0, move_line_vals))
                    available_amount -= account_group['balance']
                    if available_amount <= 0:
                        break
            if move_lines:
                move.write({'line_ids': move_lines})
            # Make reconciliation
            for move_line in move.line_ids:
                to_reconcile = move_line + self.filtered(
                    lambda x: x.account_id == move_line.account_id)
                to_reconcile.reconcile()
            move.post()
            # End of Change
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))
