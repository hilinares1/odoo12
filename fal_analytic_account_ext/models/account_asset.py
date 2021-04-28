# -*- coding: utf-8 -*-
from odoo import models, api


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        res = super(AccountAssetDepreciationLine, self).create_move(post_move)
        created_moves = self.env['account.move']
        analytic_account_id = False
        for line in self:
            analytic_account_id = line.asset_id.account_analytic_id
        if res:
            for move in created_moves.browse(res):
                move.line_ids.write({
                    'analytic_account_id': analytic_account_id.id,
                })
        return res

# end of AccountAssetDepreciationLine
