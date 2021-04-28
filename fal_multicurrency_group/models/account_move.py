from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends(
        'debit', 'credit', 'date', 'company_currency_id', 'group_currency_id'
    )
    def _amount_all_to_group_curr(self):
        cur_obj = self.env['res.currency']
        amount_total_debit = 0.0
        amount_total_credit = 0.0
        for order in self:
            amount_debit = 0.0
            amount_credit = 0.0
            # Define Self Currency
            self_currency = order.company_currency_id or order.company_id.currency_id
            curr_id = order.company_id.group_currency_id or self_currency

            for line in cur_obj.browse(curr_id):
                amount_debit += abs(order.debit)
                amount_credit += abs(order.credit)
                if self_currency != curr_id:
                    currency_id = self_currency.with_context(date=order.date)
                    amount_total_debit = currency_id._convert(
                        amount_debit,
                        curr_id,
                        order.company_id,
                        order.date
                    )
                    amount_total_credit = currency_id._convert(
                        amount_credit,
                        curr_id,
                        order.company_id,
                        order.date
                    )
                else:
                    amount_total_debit = amount_debit
                    amount_total_credit = amount_credit
            order.fal_debit_group_curr = amount_total_debit
            order.fal_credit_group_curr = amount_total_credit
            order.fal_balance_group_curr = amount_total_debit - amount_total_credit

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    @api.one
    @api.depends('tax_base_amount', 'group_currency_id', 'company_currency_id')
    def _compute_tax_base_amount_group_curr(self):
        for move_line in self:
            self_currency = move_line.company_currency_id or move_line.company_id.currency_id
            curr_id = move_line.company_id.group_currency_id or self_currency
            if self_currency != curr_id:
                currency_id = self_currency.with_context(date=move_line.date)
                self.fal_tax_base_amount_group_curr = currency_id._convert(
                    move_line.tax_base_amount,
                    curr_id,
                    move_line.company_id,
                    move_line.date
                )
            else:
                self.fal_tax_base_amount_group_curr = move_line.tax_base_amount

    @api.one
    @api.depends('amount_residual', 'group_currency_id', 'company_currency_id')
    def _amount_residual_group_curr(self):
        for move_line in self:
            self_currency = move_line.company_currency_id or move_line.company_id.currency_id
            curr_id = move_line.company_id.group_currency_id or self_currency
            if self_currency != curr_id:
                currency_id = self_currency.with_context(date=move_line.date)
                self.fal_amount_residual_group_curr = currency_id._convert(
                    move_line.amount_residual,
                    curr_id,
                    move_line.company_id,
                    move_line.date
                )
            else:
                self.fal_amount_residual_group_curr = move_line.amount_residual

    @api.one
    @api.depends('date', 'group_currency_id', 'company_currency_id')
    def _get_group_currency_rate(self):
        for move_line in self:
            self_currency = move_line.company_currency_id or move_line.company_id.currency_id
            curr_id = move_line.company_id.group_currency_id or self_currency
            if self_currency != curr_id:
                self.fal_move_date_currency_rate = curr_id._get_conversion_rate(self_currency, curr_id, move_line.company_id, move_line.date)
            else:
                self.fal_move_date_currency_rate = 1

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    fal_move_date_currency_rate = fields.Float(
        string='IFRS Currency Rate',
        track_visibility='always',
        store=True,
        compute=_get_group_currency_rate,
    )
    fal_debit_group_curr = fields.Monetary(
        compute='_amount_all_to_group_curr',
        string='Debit IFRS',
        help="Debit in IFRS Currency.",
        store=True,
        currency_field='group_currency_id',
    )
    fal_credit_group_curr = fields.Monetary(
        compute='_amount_all_to_group_curr',
        string='Credit IFRS',
        help="Credit in IFRS Currency.",
        store=True,
        currency_field='group_currency_id',
    )
    fal_balance_group_curr = fields.Monetary(
        compute='_amount_all_to_group_curr',
        string='Balance IFRS',
        help="Balance in IFRS Currency.",
        store=True,
        currency_field='group_currency_id',
    )
    fal_tax_base_amount_group_curr = fields.Monetary(string="Base Amount IFRS Currency", compute='_compute_tax_base_amount_group_curr', currency_field='group_currency_id', store=True)
    fal_amount_residual_group_curr = fields.Monetary(compute='_amount_residual_group_curr', string='Residual Amount IFRS Currency', store=True, currency_field='group_currency_id', help="The residual amount on a journal item expressed in the IFRS currency.")


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    @api.multi
    @api.depends('company_id', 'company_id.group_currency_id')
    def _get_group_currency(self):
        for move_line in self:
            move_line.group_currency_id = move_line.company_id.group_currency_id or move_line.company_id.currency_id

    group_currency_id = fields.Many2one(
        'res.currency',
        string='IFRS Currency',
        track_visibility='always',
        store=True,
        compute=_get_group_currency,
    )
    fal_amount_group_curr = fields.Monetary(
        compute='_amount_all_to_group_curr',
        string='Amount Group',
        help="Amount in IFRS Currency.",
        store=True,
        currency_field='group_currency_id',
    )

    @api.depends(
        'amount', 'company_currency_id', 'group_currency_id', 'max_date'
    )
    def _amount_all_to_group_curr(self):
        cur_obj = self.env['res.currency']
        amount_total = 0.0
        for partial in self:
            amount = 0.0
            # Define Self Currency
            self_currency = partial.company_currency_id or partial.company_id.currency_id
            curr_id = partial.company_id.group_currency_id or self_currency

            for line in cur_obj.browse(curr_id):
                amount += abs(partial.amount)
                if self_currency != curr_id:
                    currency_id = self_currency.with_context(date=partial.max_date)
                    amount_total = currency_id._convert(
                        amount,
                        curr_id,
                        partial.company_id,
                        partial.max_date
                    )
                else:
                    amount_total = amount
            partial.fal_amount_group_curr = amount_total

# end of account_move_line()
