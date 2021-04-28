# -*- coding: utf-8 -*-

from odoo import models, fields, api
import collections

JOURNAL_DOMAIN = ['|', ('type', 'in', ('bank', 'cash')),
                '&', ('type', '=', 'general'), ('is_netting', '=', True)]
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)


class account_abstract_payment(models.AbstractModel):
    _inherit = "account.abstract.payment"

    # show list of journal which type is bank or cash
    # or general with is_netting is True
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
        domain=JOURNAL_DOMAIN)

    # full overrideto inject netting feature
    # we override the onchange method, not _compute_journal_domain_and_types()
    # because odoo update the domain to ['bank', 'cash'] in hard string in 
    # _onchange_payment_type
    @api.onchange('amount', 'currency_id')
    def _onchange_amount(self):
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        domain_on_types = [('type', 'in', list(journal_types))]

        # netting modification start
        # if journal types is ('bank', 'cash'), replace domain with netting domain
        if compare(journal_types, ('bank', 'cash')):
            journal_types = ('bank', 'cash', 'general')
            domain_on_types = JOURNAL_DOMAIN
        # netting modification end

        if self.journal_id.type not in journal_types:
            self.journal_id = self.env['account.journal'].search(domain_on_types, limit=1)
        return {'domain': {'journal_id': jrnl_filters['domain'] + domain_on_types}}

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
            else:
                self.partner_type = False
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        jrnl_filters = self._compute_journal_domain_and_types()
        # modification for netting start

        # journal_types = jrnl_filters['journal_types']
        # journal_types.update(['bank', 'cash'])
        # res['domain']['journal_id'] = jrnl_filters['domain'] + [('type', 'in', list(journal_types))]
        
        journal_types = jrnl_filters['journal_types']
        odoo_domain = [('type', 'in', list(journal_types))]
        netting_domain = ['|'] + domain + JOURNAL_DOMAIN
        res['domain']['journal_id'] = jrnl_filters['domain'] + netting_domain
        # modification for netting end
        return res

class account_payment(models.Model):
    _inherit = "account.payment"

    # show list of journal which type is bank or cash
    # or general with is_netting is True
    destination_journal_id = fields.Many2one('account.journal', string='Transfer To',
        domain=JOURNAL_DOMAIN)
