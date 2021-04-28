from odoo import api, fields, models, _
from odoo.exceptions import UserError,Warning
import logging

_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_api_id = fields.Many2one("account.bank.api", string="Bank Api")
    # bank_api_id = fields.Many2one('rm.department', ondelete='cascade', string="Department", required=True)

    @api.multi
    def import_statement_api(self):
        if not self.bank_api_id:
            raise Warning(_('Please configure bank api'))
        elif self.bank_api_id.state == 'draft':
            raise Warning(_('Please confirm bank api'))
        elif not self.bank_account_id:
            raise Warning(_('Please configure bank account'))
        elif not self.bank_id:
            raise Warning(_('Please configure bank'))
        elif not self.bank_id.bic:
            raise UserError(_('Please configure bank BIC'))
        elif self.check_bic():
            return self.launch_bank_api_date_wizard()
        else:
            raise UserError(_('Api for this BIC does not exist'))

    def check_bic(self):
        # bic_dict{'BCA':'CENAIDJA'}
        # if self.bank_id.bic in bic_dict:
        if self.bank_id.bic == 'CENAIDJA':
            return True
        else:
            return False

    @api.model
    def bank_api_import_statement(self):
        _logger.info('journal.id')
        validated_journal = self.env['account.journal']
        # validated_journal = self.env['account.journal'].search([['state', '=', 'confirm']])

        for journal in validated_journal:
            _logger.info(journal.id)
        # Check bank account and get statement (Loop)
        # for bank_api in confirmed_bank_api :
        #     bic = bank_api.bank_account_id.bank_id.bic or False
        #     if not bic:
        #         raise UserError(_('Please configure bank BIC'))
        #     elif bic == 'CENAIDJA' :
        #         bank_api.bca_procedure_get_bank_statement()
        #     else:
        #         raise UserError(_('Does not implemented yet'))

    @api.multi
    def launch_bank_api_date_wizard(self):
        #Launch wizard
        # new_wizard = self.env['account.bank.api.date'].create({})
        view_id = self.env.ref('bank_api.bank_api_date_form_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Bank Statement Periode'),
            'view_mode': 'form',
            'res_model': 'account.bank.api.date',
            'target': 'new',
            # 'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
            'context': {'active_id': self.id},
        }
