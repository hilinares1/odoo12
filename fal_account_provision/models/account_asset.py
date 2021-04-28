from odoo import api, models, fields, _
from odoo.tools import float_compare


class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    type = fields.Selection([
        ('sale', 'Sale: Revenue Recognition'),
        ('purchase', 'Purchase: Asset'),
        ('cost', 'Deferred Cost'),
        ('provision', 'Provision')],
        required=True, index=True, default='purchase')

    @api.onchange('account_depreciation_id')
    def fal_onchange_depreciation_id(self):
        if self.type == 'provision':
            self.account_asset_id = self.account_depreciation_id


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    def _return_provision_view(self, move_ids):
        name = _('Provision Move')
        view_mode = 'form'
        if len(move_ids) > 1:
            name = _('Provision Moves')
            view_mode = 'tree,form'
        return {
            'name': name,
            'view_type': 'form',
            'view_mode': view_mode,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': move_ids[0],
        }

    def _get_provision_moves(self):
        move_ids = []
        for prov in self:
            unposted_depreciation_line_ids = prov.depreciation_line_ids.filtered(lambda x: not x.move_check)
            if unposted_depreciation_line_ids:
                old_values = {
                    'method_end': prov.method_end,
                    'method_number': prov.method_number,
                }

                # Remove all unposted depr. lines
                commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

                # Create a new depr. line with the residual amount and post it
                sequence = len(prov.depreciation_line_ids) - len(unposted_depreciation_line_ids) + 1
                today = fields.Datetime.today()
                vals = {
                    'amount': prov.value - prov.value_residual,
                    'asset_id': prov.id,
                    'sequence': sequence,
                    'name': (prov.code or '') + '/' + str(sequence),
                    'remaining_value': 0,
                    'depreciated_value': prov.value - prov.salvage_value,  # the asset is completely depreciated
                    'depreciation_date': today,
                }
                commands.append((0, False, vals))
                prov.write({'depreciation_line_ids': commands, 'method_end': today, 'method_number': sequence})
                tracked_fields = self.env['account.asset.asset'].fields_get(['method_number', 'method_end'])
                changes, tracking_value_ids = prov._message_track(tracked_fields, old_values)
                if changes:
                    prov.message_post(subject=_('Close Provision. Accounting entry awaiting for validation.'), tracking_value_ids=tracking_value_ids)
                move_ids += prov.depreciation_line_ids[-1].create_move_prov(post_move=False)

        return move_ids

    @api.multi
    def close_provision(self):
        move_ids = self._get_provision_moves()
        if move_ids:
            return self._return_provision_view(move_ids)
        # Fallback, as if we just clicked on the smartbutton
        return self.open_entries()


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move_prov(self, post_move=True):
        created_moves = self.env['account.move']
        for line in self:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry. Please post or delete it.'))
            move_vals = self._prepare_move_prov(line)
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    def _prepare_move_prov(self, line):
        category_id = line.asset_id.category_id
        account_analytic_id = line.asset_id.account_analytic_id
        analytic_tag_ids = line.asset_id.analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
        company_currency = line.asset_id.company_id.currency_id
        current_currency = line.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            line.amount, company_currency, line.asset_id.company_id, depreciation_date)
        asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
        }
        move_line_2 = {
            'name': asset_name,
            'account_id': category_id.account_depreciation_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': line.asset_id.partner_id.id,
            'analytic_account_id': account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and line.amount or 0.0,
        }
        move_vals = {
            'ref': line.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        return move_vals
