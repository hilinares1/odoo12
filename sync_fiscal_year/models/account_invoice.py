# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, exceptions, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _get_period(self):
        ctx = dict(self._context)
        period_ids = []
        check_period_ids = self.env['account.period'].search([])
        if check_period_ids:
            period_ids = self.env['account.period'].with_context(ctx).find()
        return period_ids and period_ids[0] or False

    period_id = fields.Many2one('account.period', string='Force Period',
        domain=[('state', '!=', 'done')],
        help="Keep empty to use the period of the validation(invoice) date.",
        readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self._get_period(), copy=False)

    @api.model
    def create(self, vals):
        if vals.get('date_invoice') and not vals.get('period_id'):
            period_id = self.env['account.period'].search([('state', '!=', 'done'), ('date_start', '<=' , vals.get('date_invoice')), ('date_stop', '>=', vals.get('date_invoice')), ('company_id', '=', self.env.user.company_id.id)], limit=1) 
            if period_id:
                vals.update({'period_id': period_id.id})
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('date_invoice'):
            period_id = self.env['account.period'].search([('state', '!=', 'done'), ('date_start', '<=' , vals.get('date_invoice')), ('date_stop', '>=', vals.get('date_invoice')), ('company_id', '=', self.env.user.company_id.id)], limit=1) 
            if period_id:
                vals.update({'period_id': period_id.id})
        return super(AccountInvoice, self).write(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
