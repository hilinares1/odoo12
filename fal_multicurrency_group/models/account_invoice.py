from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'date_invoice', 'state')
    def _amount_untaxed_usd(self):
        for item in self:
            group_curr = item.group_currency_id
            if item.currency_id != group_curr:
                item.untaxed_amount_group_curr = item.currency_id._convert(item.amount_untaxed, group_curr, item.company_id, item.date_invoice or fields.Date.today())
                item.amount_tax_group_curr = item.currency_id._convert(item.amount_tax, group_curr, item.company_id, item.date_invoice or fields.Date.today())
                item.amount_total_group_curr = item.currency_id._convert(item.amount_total, group_curr, item.company_id, item.date_invoice or fields.Date.today())
            else:
                item.untaxed_amount_group_curr = item.amount_untaxed
                item.amount_tax_group_curr = item.amount_tax
                item.amount_total_group_curr = item.amount_total

    @api.depends('state', 'currency_id', 'invoice_line_ids.price_subtotal', 'move_id.line_ids.amount_residual', 'move_id.line_ids.currency_id')
    def _amount_ballance_usd(self):
        for invoice in self:
            residual = 0.0
            group_curr = invoice.group_currency_id
            for line in invoice.sudo().move_id.line_ids:
                if line.account_id.internal_type in ('receivable', 'payable'):
                    if line.currency_id == line.currency_id:
                        residual += line.amount_residual_currency if \
                            line.currency_id else line.amount_residual
                    else:
                        from_currency = (
                            line.currency_id and line.currency_id.with_context(
                                date=line.date)
                        ) or line.company_id.currency_id.with_context(
                            date=line.date)
                        residual += from_currency._convert(
                            line.amount_residual, group_curr, self.company_id, line.date or fields.Date.today())
                line.amount_ballance_usd = abs(residual)

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for invoice in self:
            invoice.group_currency_id = invoice.company_id.group_currency_id or invoice.company_id.currency_id

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    untaxed_amount_group_curr = fields.Monetary(
        compute='_amount_untaxed_usd',
        string='IFRS Untaxed Amount',
        track_visibility='always',
        store=True,
        currency_field='group_currency_id',
    )
    amount_tax_group_curr = fields.Monetary(
        compute='_amount_untaxed_usd',
        string='IFRS Tax',
        track_visibility='always',
        store=True,
        currency_field='group_currency_id',
    )
    amount_total_group_curr = fields.Monetary(
        compute='_amount_untaxed_usd',
        string='IFRS Total',
        help="The total amount in Group Currency.",
        store=True,
        currency_field='group_currency_id',
    )
    amount_ballance_group_curr = fields.Monetary(
        compute='_amount_ballance_usd',
        string='IFRS Balance',
        help="The balance amount in Group Currency.",
        store=True,
        currency_field='group_currency_id',
    )

# end of account_invoice()
