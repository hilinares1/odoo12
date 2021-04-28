# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def create(self, vals):
        res = super(AccountJournal, self).create(vals)
        list_data = ['Cash','Bank','Liquidity Transfer','Undistributed Profits/Losses']
        fal_account_for_delete = self.env['account.account'].search([('name','in',list_data)])
        for account_delete in fal_account_for_delete:
        	account_delete.unlink()
        	
        return res
