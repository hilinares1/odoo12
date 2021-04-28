from odoo import api, fields, models
from datetime import datetime


class FalInvoiceTermLine(models.Model):
    _inherit = 'fal.invoice.term.line'

    # Or to Purchase Order, it may only has order id
    fal_po_id = fields.Many2one("purchase.order", string="Purchase Order Id")
    # Or also a line
    fal_purchase_order_id = fields.Many2one(
        "purchase.order", related="fal_purchase_order_line_id.order_id",
        string="Purchase Order", store=True)
    fal_purchase_order_line_id = fields.Many2one(
        "purchase.order.line", string="Purchase Order Line")

    @api.one
    @api.depends('sequence', 'date', 'fal_invoice_term_id')
    def _compute_is_final(self):
        res = super(FalInvoiceTermLine, self)._compute_is_final()
        if self.fal_purchase_order_line_id:
            last_invoice_term = False
            # We trust odoo order to make the last sequence as Final
            for invoice_term_line in self.fal_purchase_order_line_id.fal_invoice_milestone_line_date_ids:
                invoice_term_line.is_final = False
                last_invoice_term = invoice_term_line
            if last_invoice_term:
                last_invoice_term.is_final = True
        return res

    @api.model
    def _cron_generate_invoice_po_line_by_planning_date(self):
        return self._generate_invoice_po_line_by_planning_date()

    @api.multi
    def _generate_invoice_po_line_by_planning_date(self):
        current_date = datetime.now()
        advance_wizard_obj = self.env['purchase.advance.payment.inv']
        res = False
        if self.ids:
            term_line_ids = self.browse(self.ids)
        else:
            term_line_ids = self.search([
                ('date', '<=', current_date),
                ('fal_purchase_order_line_id', '!=', False),
                ('invoice_id', '=', False),
                ('fal_purchase_order_id.state', '=', 'purchase')])
        if term_line_ids:
            for term_line in term_line_ids:
                orderline = term_line.fal_purchase_order_line_id
                order = orderline.order_id
                if not term_line.is_final:
                    # Call Odoo downpayment Wizard function
                    wizard_vals = {
                        'advance_payment_method': 'percentage',
                        'amount': term_line.percentage,
                        'product_id': term_line.product_id.id,
                        'description': term_line.product_id.name

                    }
                    advPmnt = advance_wizard_obj.create(wizard_vals)
                    advPmnt.with_context({
                        'active_ids': [order.id],
                        'po_line': orderline,
                        'term_line': term_line}).fal_milestone_create_invoices()
                else:
                    # Call Odoo downpayment Wizard function
                    wizard_vals = {
                        'advance_payment_method': 'all',
                    }
                    advPmnt = advance_wizard_obj.create(wizard_vals)
                    advPmnt.with_context({
                        'active_ids': [order.id],
                        'po_line': orderline,
                        'term_line': term_line}).fal_milestone_create_invoices()

            purchase_order = term_line_ids.mapped('fal_purchase_order_id')
            for purchase in purchase_order:
                _type = []
                res = {}
                for term in term_line_ids.filtered(lambda a: a.fal_purchase_order_id == purchase):
                    _type.append((term.date, term))
                for date, val in _type:
                    if date in res:
                        res[date] += val
                    else:
                        res[date] = val
                for key in res:
                    for term_id in res[key]:
                        term_id.invoice_id.invoice_line_ids.write({'invoice_id': res[key][0].invoice_id.id})
                        if term_id != res[key][0]:
                            term_id.invoice_id.unlink()
                            term_id.write({'invoice_id': res[key][0].invoice_id.id})
        return res
