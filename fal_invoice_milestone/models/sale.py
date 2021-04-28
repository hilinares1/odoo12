from odoo import api, fields, models, _
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Rules', domain=[('is_template', '=', False)])
    fal_invoice_term_type = fields.Selection(
        'Invoice Term Type', related='fal_invoice_term_id.type')
    fal_invoice_milestone_line_date_ids = fields.One2many(
        "fal.invoice.term.line", "fal_order_id",
        string="Term Lines", copy=True)
    fal_milestone_by_cron = fields.Boolean("Auto Run Invoice Milestone")
    fal_invoice_rules = fields.Selection([
        ('milestone', 'Invoice Milestone'),
        ('subscription', 'Subscription'),
    ], string='Rules', related='fal_invoice_term_id.fal_invoice_rules', store=True)
    fal_invoice_rules_type = fields.Selection([
        ('percentage', 'By percentage'),
        ('amount', 'By Exact Amount'),
    ], string="Rules Type", related='fal_invoice_term_id.fal_invoice_rules_type', store=True)

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order_line in self.order_line.filtered(lambda r: len(
                r.fal_invoice_term_id) > 0):
            temp = 0.0
            for invoice_milestone_line in order_line.fal_invoice_milestone_line_date_ids:
                temp += invoice_milestone_line.percentage
            if temp > 100:
                raise UserError(_(
                    "Total Percentage %s cannot be greater than 100"
                ) % (order_line.product_id.display_name))
            if temp < 100:
                raise UserError(_(
                    "Total Percentage %s cannot be lower than 100"
                ) % (order_line.product_id.display_name))
        return res

    # duplicate function odoo to split downpayment
    @api.multi
    def fal_milestone_action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        invoices_origin = {}
        invoices_name = {}
        original_term_line = self._context.get("term_line", False)

        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)

            # We only want to create sections that have at least one invoiceable line
            pending_section = None

            # Create lines in batch to avoid performance problems
            line_vals_list = []
            order_line = [self._context.get('so_line')]
            for item in self._context.get('so_line').fal_invoice_milestone_line_date_ids.filtered(lambda a: not a.is_final):
                for invoice in item.invoice_id.invoice_line_ids:
                    order_line.append(invoice.sale_line_ids)
            for line in order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoices_origin[group_key] = [invoice.origin]
                    invoices_name[group_key] = [invoice.name]
                elif group_key in invoices:
                    if order.name not in invoices_origin[group_key]:
                        invoices_origin[group_key].append(order.name)
                    if order.client_order_ref and order.client_order_ref not in invoices_name[group_key]:
                        invoices_name[group_key].append(order.client_order_ref)

                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        line_vals_list.extend(pending_section.invoice_line_create_vals(
                            invoices[group_key].id,
                            pending_section.qty_to_invoice
                        ))
                        pending_section = None
                    line_vals_list.extend(line.invoice_line_create_vals(
                        invoices[group_key].id, line.qty_to_invoice
                    ))

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order

            self.env['account.invoice.line'].create(line_vals_list)

        for group_key in invoices:
            invoices[group_key].write({'name': ', '.join(invoices_name[group_key]),
                                       'origin': ', '.join(invoices_origin[group_key])})
            sale_orders = references[invoices[group_key]]
            if len(sale_orders) == 1:
                invoices[group_key].reference = sale_orders.reference

        if not invoices:
            raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        for invoice in invoices.values():
            invoice.compute_taxes()
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_total < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            # Idem for partner
            so_payment_term_id = invoice.payment_term_id.id
            fp_invoice = invoice.fiscal_position_id
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = fp_invoice
            # To keep the payment terms set on the SO
            invoice.payment_term_id = so_payment_term_id
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
            if original_term_line and invoice.id:
                original_term_line.invoice_id = invoice.id
        return [inv.id for inv in invoices.values()]

    # Set Invoice Term based on analytic account id
    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id:
            self.fal_invoice_term_id = \
                self.analytic_account_id.fal_invoice_term_id

    # If Invoice Term is set, Create Term Line
    # based on the selected Invoice Term
    # change this to button compute
    # @api.onchange('fal_invoice_term_id')
    # def onchange_fal_invoice_term_id(self):
    @api.one
    def compute_fal_invoice_term_id(self):
        self.fal_invoice_milestone_line_date_ids = False

        if self.fal_invoice_term_id:
            temp = []
            val_order_date = self.date_order.date()
            if self.fal_invoice_term_id.fal_invoice_rules == 'milestone':
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    temp.append((0, 0, {
                        'parent_id': line.id,
                        'fal_order_id': self.id,
                        'fal_invoice_rules': self.fal_invoice_term_id.fal_invoice_rules,
                        'fal_invoice_rules_type': self.fal_invoice_term_id.fal_invoice_rules_type,
                        'percentage': line.percentage,
                        'amount': line.amount,
                        'date': line.date,
                        'invoice_forecast_date': line.invoice_forecast_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            else:
                if self.fal_invoice_term_id.recurring_rule_type == 'daily':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                timedelta(days=int_days)
                            var_date = var_date + timedelta(days=int_days)
                        else:
                            var_date = var_date + timedelta(days=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_order_id': self.id,
                            'fal_invoice_rules': self.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': self.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'invoice_forecast_date': line.invoice_forecast_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
                elif self.fal_invoice_term_id.recurring_rule_type == 'weekly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(weeks=int_days)
                            var_date = var_date + relativedelta(weeks=int_days)
                        else:
                            var_date = var_date + relativedelta(weeks=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_order_id': self.id,
                            'fal_invoice_rules': self.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': self.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'invoice_forecast_date': line.invoice_forecast_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
                elif self.fal_invoice_term_id.recurring_rule_type == 'monthly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(months=int_days)
                            var_date = var_date + relativedelta(months=int_days)
                        else:
                            var_date = var_date + relativedelta(months=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_order_id': self.id,
                            'fal_invoice_rules': self.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': self.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'invoice_forecast_date': line.invoice_forecast_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
                elif self.fal_invoice_term_id.recurring_rule_type == 'yearly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(years=int_days)
                            var_date = var_date + relativedelta(years=int_days)
                        else:
                            var_date = var_date + relativedelta(years=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_order_id': self.id,
                            'fal_invoice_rules': self.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': self.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'invoice_forecast_date': line.invoice_forecast_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
            self.fal_invoice_milestone_line_date_ids = temp
            self.apply_milestone_to_line()

    @api.multi
    def apply_analytic_to_line(self):
        self.ensure_one()
        for line in self.order_line.filtered(lambda a: a.product_id):
            line.write({
                'fal_analytic_account_id': self.analytic_account_id.id or False
            })

    @api.multi
    def apply_milestone_to_line(self):
        self.ensure_one()
        FalInvoiceTermLine = self.env['fal.invoice.term.line']

        self.apply_analytic_to_line()
        # set order line analytic, invoice term, and milestone
        for line in self.order_line.filtered(lambda a: a.product_id):

            line.write({
                'fal_invoice_term_id': self.fal_invoice_term_id.id or False
            })

            temp = []
            for milestone in self.fal_invoice_milestone_line_date_ids:
                item = FalInvoiceTermLine.create({
                    'parent_id': milestone.parent_id.id,
                    'fal_sale_order_line_id': line.id,
                    'fal_invoice_rules': milestone.fal_invoice_rules,
                    'fal_invoice_rules_type': milestone.fal_invoice_term_id.fal_invoice_rules_type,
                    'percentage': milestone.percentage,
                    'amount': milestone.amount,
                    'date': milestone.date,
                    'sequence': milestone.sequence,
                    'product_id': milestone.product_id.id,
                    'name': milestone.name,
                    'description': milestone.description,
                    'is_final': milestone.is_final,
                })
                temp.append(item.id)

            line.write({
                'fal_invoice_milestone_line_date_ids': [(6, 0, temp)]
            })

        return True

    @api.multi
    def create_invoice_milestone_btn(self):
        self.ensure_one()
        temp_count = self.invoice_count

        FalInvoiceTermLine = self.env['fal.invoice.term.line']
        current_date = datetime.now()

        term_line_ids = FalInvoiceTermLine.search([
            ('date', '<=', current_date),
            ('fal_sale_order_id', 'in', self.ids),
            ('invoice_id', '=', False),
        ])

        term_line_ids._generate_invoice_order_line_by_planning_date()

        if self.invoice_count > temp_count:
            # new invoice is created
            return self.action_view_invoice()

        return True


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fal_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Analytic Account')
    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Rules', domain=[('is_template', '=', False)])
    fal_invoice_rules = fields.Selection([
        ('milestone', 'Invoice Milestone'),
        ('subscription', 'Subscription'),
    ], string='Rules', related='fal_invoice_term_id.fal_invoice_rules', store=True)
    fal_invoice_rules_type = fields.Selection([
        ('percentage', 'By percentage'),
        ('amount', 'By Exact Amount'),
    ], string="Rules Type", related='fal_invoice_term_id.fal_invoice_rules_type', store=True)
    fal_invoice_term_type = fields.Selection(
        'Invoice Term Type', related='fal_invoice_term_id.type')
    fal_invoice_milestone_line_date_ids = fields.One2many(
        "fal.invoice.term.line", "fal_sale_order_line_id",
        string="Term Lines", copy=True)
    fal_sequence_number = fields.Char("Sequence Number")
    #
    fal_deposit_from_sale_order_line_id = fields.Many2one(
        'sale.order.line', 'Deposit from Sale Order Line', copy=False)
    fal_deposit_sale_order_line_ids = fields.One2many(
        'sale.order.line', 'fal_deposit_from_sale_order_line_id',
        'Deposit Sale Order Line', copy=False)
    #

    @api.model
    def create(self, vals):
        if self.fal_invoice_term_id:
            product_id = vals['product_id']
            product = self.env['product.product'].browse(product_id)
            if product.type == 'product':
                raise UserError(_(
                    'You cannot set the milestone for \
                    the stockable product transaction'))

        return super(SaleOrderLine, self).create(vals)

    # Give Analytic Information to Invoice
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['account_analytic_id'] = self.fal_analytic_account_id \
            and self.fal_analytic_account_id.id or self.order_id.analytic_account_id.id or False
        return res

    # Set Invoice Term based on analytic account id
    @api.onchange('fal_analytic_account_id')
    def onchange_fal_analytic_account_id(self):
        if self.fal_analytic_account_id:
            self.fal_invoice_term_id = \
                self.fal_analytic_account_id.fal_invoice_term_id

    @api.onchange('fal_invoice_term_id')
    def onchange_fal_invoice_term_id(self):
        self.fal_invoice_milestone_line_date_ids = False
        if self.fal_invoice_term_id:
            temp = []
            order_date = self.order_id.date_order
            val_order_date = order_date.date()

            if self.fal_invoice_term_id.fal_invoice_rules == 'milestone':
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    temp.append((0, 0, {
                        'parent_id': line.id,
                        'fal_invoice_rules': line.fal_invoice_term_id.fal_invoice_rules,
                        'fal_invoice_rules_type': line.fal_invoice_term_id.fal_invoice_rules_type,
                        'percentage': line.percentage,
                        'amount': line.amount,
                        'date': line.date or val_order_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            else:
                if self.fal_invoice_term_id.recurring_rule_type == 'daily':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                timedelta(days=int_days)
                            var_date = var_date + timedelta(days=int_days)
                        else:
                            var_date = var_date + timedelta(days=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_invoice_rules': line.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': line.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
                elif self.fal_invoice_term_id.recurring_rule_type == 'weekly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(weeks=int_days)
                            var_date = var_date + relativedelta(weeks=int_days)
                        else:
                            var_date = var_date + relativedelta(weeks=int_days)

                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_invoice_rules': line.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': line.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))

                elif self.fal_invoice_term_id.recurring_rule_type == 'monthly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(months=int_days)
                            var_date = var_date + relativedelta(months=int_days)
                        else:
                            var_date = var_date + relativedelta(months=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_invoice_rules': line.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': line.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
                elif self.fal_invoice_term_id.recurring_rule_type == 'yearly':
                    int_days = self.fal_invoice_term_id.recurring_interval
                    var_date = val_order_date
                    for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                        if val_order_date < var_date:
                            val_order_date = val_order_date + \
                                relativedelta(years=int_days)
                            var_date = var_date + relativedelta(years=int_days)
                        else:
                            var_date = var_date + relativedelta(years=int_days)
                        temp.append((0, 0, {
                            'parent_id': line.id,
                            'fal_invoice_rules': line.fal_invoice_term_id.fal_invoice_rules,
                            'fal_invoice_rules_type': line.fal_invoice_term_id.fal_invoice_rules_type,
                            'percentage': line.percentage,
                            'amount': line.amount,
                            'date': line.date or val_order_date,
                            'sequence': line.sequence,
                            'product_id': line.product_id.id,
                            'name': line.name,
                            'description': line.description,
                            'is_final': line.is_final,
                        }))
            self.fal_invoice_milestone_line_date_ids = temp

# end of SaleOrderLine()
