from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Term')
    fal_invoice_term_type = fields.Selection(
        'Invoice Term Type', related='fal_invoice_term_id.type')
    fal_invoice_milestone_line_date_ids = fields.One2many(
        "fal.invoice.term.line", "fal_po_id",
        string="Term Lines", copy=True)

    @api.multi
    def action_confirm(self):
        res = super(PurchaseOrder, self).action_confirm()
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

    # @api.multi
    # def action_invoice_create(self, grouped=False, final=False):
    #     res = super(PurchaseOrder, self).action_invoice_create(grouped, final)
    #     # Add Invoice in the Term Line
    #     original_term_line = self._context.get("term_line", False)
    #     if original_term_line and res:
    #         original_term_line.invoice_id = res[0]
    #     return res

    # Set Invoice Term based on analytic account id
    @api.onchange('account_analytic_id')
    def onchange_account_analytic_id(self):
        if self.account_analytic_id:
            self.fal_invoice_term_id = \
                self.account_analytic_id.fal_invoice_term_id

    # If Invoice Term is set, Create Term Line
    # based on the selected Invoice Term
    @api.onchange('fal_invoice_term_id')
    def onchange_fal_invoice_term_id(self):
        self.fal_invoice_milestone_line_date_ids = False

        if self.fal_invoice_term_id:
            temp = []
            val_order_date = self.date_order.date()
            val_date = val_order_date
            if self.fal_invoice_term_id.type == 'date':
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    temp.append((0, 0, {
                        'fal_po_id': self.id,
                        'percentage': line.percentage,
                        'date': line.date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            elif self.fal_invoice_term_id.type == 'number_of_days':
                int_days = self.fal_invoice_term_id.interval_day
                var_date = val_order_date
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            timedelta(days=int_days)
                        var_date = var_date + relativedelta(months=10)
                    else:
                        var_date = var_date + relativedelta(months=10)
                    temp.append((0, 0, {
                        'fal_po_id': self.id,
                        'percentage': line.percentage,
                        'date': val_order_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            elif self.fal_invoice_term_id.type == 'date_monthly':
                temp = []
                int_months = 1
                int_days = self.fal_invoice_term_id.start_day
                var_date = val_date
                try:
                    val_date = val_date.replace(day=int_days)
                except Exception:
                    try:
                        val_date = val_date.replace(day=int_days - 1)
                    except Exception:
                        try:
                            val_date = val_date.replace(day=int_days - 2)
                        except Exception:
                            try:
                                val_date = val_date.replace(day=int_days - 3)
                            except Exception:
                                pass
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_date < var_date:
                        val_date = val_date + relativedelta(months=int_months)
                        var_date = var_date + relativedelta(months=10)
                    else:
                        var_date = var_date + relativedelta(months=10)
                    try:
                        val_date = val_date.replace(day=int_days)
                    except Exception:
                        pass

                    temp.append((0, 0, {
                        'fal_po_id': self.id,
                        'percentage': line.percentage,
                        'date': val_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))

            elif self.fal_invoice_term_id.type == 'date_yearly':
                temp = []
                int_year = 1
                int_months = self.fal_invoice_term_id.start_month
                int_days = self.fal_invoice_term_id.start_day
                var_date = val_date
                val_date = val_date.replace(month=int_months)
                try:
                    val_date = val_date.replace(day=int_days)
                except Exception:
                    try:
                        val_date = val_date.replace(day=int_days - 1)
                    except Exception:
                        try:
                            val_date = val_date.replace(day=int_days - 2)
                        except Exception:
                            try:
                                val_date = val_date.replace(day=int_days - 3)
                            except Exception:
                                pass
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_date < var_date:
                        val_date = val_date + relativedelta(years=int_year)
                        var_date = var_date + relativedelta(years=10)
                    else:
                        var_date = var_date + relativedelta(years=10)
                    try:
                        val_date = val_date.replace(day=int_days)
                    except Exception:
                        pass
                    temp.append((0, 0, {
                        'fal_po_id': self.id,
                        'percentage': line.percentage,
                        'date': val_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            self.fal_invoice_milestone_line_date_ids = temp

    @api.multi
    def apply_analytic_to_line(self):
        self.ensure_one()
        for line in self.order_line:
            line.write({
                'account_analytic_id': self.account_analytic_id.id or False
            })

    @api.multi
    def apply_milestone_to_line(self):
        self.ensure_one()
        FalInvoiceTermLine = self.env['fal.invoice.term.line']

        self.apply_analytic_to_line()
        # set order line analytic, invoice term, and milestone
        for line in self.order_line:
            line.write({
                'account_analytic_id': self.account_analytic_id.id or False
            })
            line.write({
                'fal_invoice_term_id': self.fal_invoice_term_id.id or False
            })

            temp = []
            for milestone in self.fal_invoice_milestone_line_date_ids:
                item = FalInvoiceTermLine.create({
                    'fal_purchase_order_line_id': line.id,
                    'percentage': milestone.percentage,
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
        FalInvoiceTermLine._cron_generate_invoice_po_line_by_planning_date()

        if self.invoice_count > temp_count:
            # new invoice is created
            return self.action_view_invoice()

        return True


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fal_invoice_term_id = fields.Many2one('fal.invoice.term', 'Invoice Term')
    fal_invoice_term_type = fields.Selection(
        'Invoice Term Type', related='fal_invoice_term_id.type')
    fal_invoice_milestone_line_date_ids = fields.One2many(
        "fal.invoice.term.line", "fal_purchase_order_line_id",
        string="Term Lines", copy=True)
    fal_sequence_number = fields.Char("Sequence Number")

    fal_deposit_from_purchase_order_line_id = fields.Many2one(
        'purchase.order.line', 'Deposit from urchase Order Line', copy=False)
    fal_deposit_purchase_order_line_ids = fields.One2many(
        'purchase.order.line', 'fal_deposit_from_purchase_order_line_id',
        'Deposit Purchase Order Line', copy=False)

    @api.model
    def create(self, vals):
        if self.fal_invoice_term_id:
            product_id = vals['product_id']
            product = self.env['product.product'].browse(product_id)
            if product.type == 'product':
                raise UserError(_(
                    'You cannot set the milestone for \
                    the stockable product transaction'))

        return super(PurchaseOrderLine, self).create(vals)

    # Give Analytic Information to Invoice
    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(PurchaseOrderLine, self)._prepare_invoice_line(qty)
        res['account_analytic_id'] = self.account_analytic_id \
            and self.account_analytic_id.id or False
        return res

    # Set Invoice Term based on analytic account id
    @api.onchange('account_analytic_id')
    def onchange_account_analytic_id(self):
        if self.account_analytic_id:
            self.fal_invoice_term_id = \
                self.account_analytic_id.fal_invoice_term_id

    # If Invoice Term is set, Create Term Line
    # based on the selected Invoice Term
    @api.onchange('fal_invoice_term_id')
    def onchange_fal_invoice_term_id(self):
        self.fal_invoice_milestone_line_date_ids = False
        if self.fal_invoice_term_id:
            temp = []
            order_date = self.order_id.date_order
            # product = self.fal_invoice_term_id.product_id
            val_order_date = order_date.date()
            val_date = val_order_date

            if self.fal_invoice_term_id.type == 'date':
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    temp.append((0, 0, {
                        'fal_purchase_order_id': self.id,
                        'percentage': line.percentage,
                        'date': line.date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            elif self.fal_invoice_term_id.type == 'number_of_days':
                int_days = self.fal_invoice_term_id.interval_day
                var_date = val_order_date
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_order_date < var_date:
                        val_order_date = val_order_date + \
                            timedelta(days=int_days)
                        var_date = var_date + relativedelta(months=10)
                    else:
                        var_date = var_date + relativedelta(months=10)
                    temp.append((0, 0, {
                        'fal_purchase_order_id': self.id,
                        'percentage': line.percentage,
                        'date': val_order_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            elif self.fal_invoice_term_id.type == 'date_monthly':
                temp = []
                int_months = 1
                int_days = self.fal_invoice_term_id.start_day
                var_date = val_date
                try:
                    val_date = val_date.replace(day=int_days)
                except Exception:
                    try:
                        val_date = val_date.replace(day=int_days - 1)
                    except Exception:
                        try:
                            val_date = val_date.replace(day=int_days - 2)
                        except Exception:
                            try:
                                val_date = val_date.replace(day=int_days - 3)
                            except Exception:
                                pass
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_date < var_date:
                        val_date = val_date + relativedelta(months=int_months)
                        var_date = var_date + relativedelta(months=10)
                    else:
                        var_date = var_date + relativedelta(months=10)
                    try:
                        val_date = val_date.replace(day=int_days)
                    except Exception:
                        pass

                    temp.append((0, 0, {
                        'fal_purchase_order_id': self.id,
                        'percentage': line.percentage,
                        'date': val_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))

            elif self.fal_invoice_term_id.type == 'date_yearly':
                temp = []
                int_year = 1
                int_months = self.fal_invoice_term_id.start_month
                int_days = self.fal_invoice_term_id.start_day
                var_date = val_date
                val_date = val_date.replace(month=int_months)
                try:
                    val_date = val_date.replace(day=int_days)
                except Exception:
                    try:
                        val_date = val_date.replace(day=int_days - 1)
                    except Exception:
                        try:
                            val_date = val_date.replace(day=int_days - 2)
                        except Exception:
                            try:
                                val_date = val_date.replace(day=int_days - 3)
                            except Exception:
                                pass
                for line in self.fal_invoice_term_id.fal_invoice_term_line_ids:
                    if val_date < var_date:
                        val_date = val_date + relativedelta(years=int_year)
                        var_date = var_date + relativedelta(years=10)
                    else:
                        var_date = var_date + relativedelta(years=10)
                    try:
                        val_date = val_date.replace(day=int_days)
                    except Exception:
                        pass
                    temp.append((0, 0, {
                        'fal_purchase_order_id': self.id,
                        'percentage': line.percentage,
                        'date': val_date,
                        'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'description': line.description,
                        'is_final': line.is_final,
                    }))
            self.fal_invoice_milestone_line_date_ids = temp

# end of PurchaseOrderLine()
