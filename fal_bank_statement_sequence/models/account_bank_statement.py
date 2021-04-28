from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_statement_sequence_id = fields.Many2one('ir.sequence', string='Statement Sequence',
        help="This field contains the information related to the numbering of the statement of this journal.", copy=False)

    @api.model
    def _create_sequence(self, vals, refund=False):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_sequence_prefix(vals['code'], refund)
        seq_name = refund and vals['code'] + _(': Refund') or vals['code']
        # CLuedoo Add-ons
        if self._context.get('statement', False):
            seq_name += _(': Statement')
            prefix += _('Statement/')
        # End CLuedoo Add-ons
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = refund and vals.get('refund_sequence_number_next', 1) or vals.get('sequence_number_next', 1)
        return seq

    @api.multi
    def write(self, vals):
        for journal in self:
            if ('code' in vals and journal.code != vals['code']):
                new_prefix = self._get_sequence_prefix(vals['code'], refund=False)
                new_prefix += _('Statement/')
                journal.bank_statement_sequence_id.write({'prefix': new_prefix})
        result = super(AccountJournal, self).write(vals)
        return result

    @api.model
    def create(self, vals):
        # CLuedoo Add-ons
        # We just need to create the relevant sequences according to the chosen options
        if vals.get('type') in ('bank', 'cash') and not vals.get('bank_statement_sequence_id'):
            vals.update({'bank_statement_sequence_id': self.sudo().with_context({'statement': True})._create_sequence(vals, refund=False).id})
        # End CLuedoo Add-ons
        return super(AccountJournal, self).create(vals)


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            journal_id = vals.get('journal_id', self._context.get('default_journal_id', False))
            journal = self.env['account.journal'].browse(journal_id)
            if journal.bank_statement_sequence_id:
                vals['name'] = journal.bank_statement_sequence_id.with_context(ir_sequence_date=vals.get('date')).next_by_id()
        return super(AccountBankStatement, self).create(vals)
