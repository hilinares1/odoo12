# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError


class hr_timesheet_invoice_create(models.TransientModel):
    _name = 'hr.timesheet.invoice.create'
    _description = 'Create invoice from timesheet'

    @api.multi
    def do_create(self):
        # Create an invoice based on selected timesheet lines
        analytic_line_obj = self.env['account.analytic.line']
        invoice_obj = self.env['account.invoice']
        invs = []
        invoices = {}
        for analytic_line in analytic_line_obj.browse(
                self.env.context.get('active_ids', False)):
            if not analytic_line.to_invoice:
                raise UserError(_(
                    'Trying to invoice non invoiceable line for %s.'
                ) % (analytic_line.product_id.name))
            if analytic_line.timesheet_invoice_id:
                raise UserError(_("There's is line that already invoiced"))
            group_key = analytic_line.task_id.sale_line_id.order_id.id
            if group_key not in invoices:
                val_order = analytic_line.task_id.sale_line_id.order_id
                inv_id = invoice_obj.create(
                    analytic_line._prepare_timesheet_invoice(
                        val_order.partner_invoice_id,
                        val_order.company_id,
                        val_order.currency_id))
                invoices[group_key] = inv_id.id
                invs.append(inv_id.id)
            val_prod = analytic_line.task_id.sale_line_id.product_id
            account = val_prod.property_account_income_id \
                or val_prod.categ_id.property_account_income_categ_id
            if not account:
                raise UserError(_(
                    'Please define income account for this product: "%s" \
                    (id:%d) - or for its category: "%s".') % (
                    analytic_line.task_id.sale_line_id.product_id.name,
                    analytic_line.task_id.sale_line_id.product_id.id,
                    analytic_line.task_id.sale_line_id.product_id.categ_id.name
                ))

            val_order = analytic_line.task_id.sale_line_id.order_id
            fpos = val_order.fiscal_position_id \
                or val_order.partner_id.property_account_position_id
            if fpos:
                account = fpos.map_account(account)
            inv_line = self.env['account.invoice.line']
            val_sale_line = analytic_line.task_id.sale_line_id
            inv_line.create({
                'name': val_sale_line.name,
                'sequence': val_sale_line.sequence,
                'origin': val_sale_line.order_id.name,
                'account_id': account.id,
                'price_unit': val_sale_line.price_unit,
                'quantity': analytic_line.unit_amount_coef,
                'discount': analytic_line.to_invoice.factor,
                'uom_id': val_sale_line.product_uom.id,
                'product_id': val_sale_line.product_id.id or False,
                'invoice_line_tax_ids': [(6, 0, val_sale_line.tax_id.ids)],
                'account_analytic_id': val_order.analytic_account_id.id,
                'invoice_id': invoices[group_key],
                'sale_line_ids': [(6, 0, [val_sale_line.id])],
            })
            analytic_line.timesheet_invoice_id = invoices[group_key]

        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('account.action_invoice_tree1')
        list_view_id = imd.xmlid_to_res_id('account.invoice_tree')
        form_view_id = imd.xmlid_to_res_id('account.invoice_form')

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [
                [list_view_id, 'tree'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'kanban'],
                [False, 'calendar'],
                [False, 'pivot']
            ],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'domain': "[('id', 'in', %s)]" % invs
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
