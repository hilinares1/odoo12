from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fal_product_id = fields.Many2one('product.product', string='Product')
    fal_timesheet_analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Default Timesheet Analytic Account'
    )


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    fal_journal_id = fields.Many2one(
        'account.journal', string='Journal',
    )
    fal_move_id = fields.Many2one(
        'account.move', string='Journal Entry'
    )
    fal_accounting_date = fields.Date("Accounting Date")
    state = fields.Selection(selection_add=[('post', 'Posted')])

    @api.multi
    def action_sheet_move_create(self):
        if any(sheet.state != 'done' for sheet in self):
            raise UserError(_("You can only generate accounting entry for approved Timesheet(s)."))
        if any(not sheet.fal_journal_id for sheet in self):
            raise UserError(_("Timesheet must have an timesheet journal specified to generate accounting entries."))
        res = self.fal_create_move()
        if not self.fal_accounting_date:
            self.fal_accounting_date = self.fal_move_id.date
        if res is True:
            self.write({'state': 'post'})
        return res

    @api.multi
    def fal_create_move(self):
        for sheet in self:
            if not sheet.company_id:
                raise UserError(
                    _("No company defined in this timesheet, \
                        please define one."))
            if not self.fal_journal_id:
                raise UserError(
                    _("No journal defined in this timesheet, \
                        please define one."))
            val_tmpl = sheet.employee_id.fal_product_id.product_tmpl_id
            if not val_tmpl._get_product_accounts()['expense']:
                return {
                    'name': _('Set Product Account'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'timesheet.journal.wizard',
                    'target': 'new',
                    'context': {'default_product_id': sheet.employee_id.fal_product_id.id or self.env.ref('fal_timesheet_journal.product_timesheet_journal').id},
                }
            move_lines = sheet._move_line_get()
            total, total_currency, move_lines = sheet.compute_invoice_totals(
                sheet.company_id.currency_id, move_lines)

            total_quantity = 0
            for data in move_lines:
                total_quantity += data['quantity']

            move_lines.append({
                'type': 'dest',
                'name': sheet.employee_id.name or '/',
                'price': total,
                'product_id': sheet.employee_id.fal_product_id.id,
                'account_id': val_tmpl._get_product_accounts()['expense'].id,
                'date_maturity': fields.Date.context_today(self),
                'amount_currency': total_currency,
                'currency_id': sheet.company_id.currency_id.id,
                'quantity': total_quantity,
                'analytic_account_id': sheet.employee_id.fal_timesheet_analytic_account_id.id,
            })
            lines = map(
                lambda x: (
                    0,
                    0,
                    sheet._prepare_move_line(x)),
                move_lines)
            move = sheet.fal_move_id
            if not move:
                move = self.env['account.move'].create({
                    'journal_id': sheet.fal_journal_id.id,
                    'company_id': self.env.user.company_id.id,
                    'date': sheet.fal_accounting_date if sheet.fal_accounting_date else fields.Date.context_today(self),
                })
            else:
                move = sheet.fal_move_id
                to_remove = [
                    (2, to_remove_line.id, 0)
                    for to_remove_line in move.line_ids
                ]
                move.write({
                    'line_ids': to_remove,
                })

            move.write({
                'line_ids': lines,
            })
            move.ref = sheet.name
            move.post()
            sheet.write({'fal_move_id': move.id})
            return True

    def _prepare_move_line(self, line):
        '''
        This function prepares move line of account.move related to an expense
        '''
        partner_id = self.employee_id.address_id and self.employee_id.address_id.id or False
        return {
            'date_maturity': line.get('date_maturity'),
            'partner_id': partner_id,
            'name': line['name'][:64],
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_line_ids': line.get('analytic_line_ids'),
            'amount_currency': line['price'] > 0 and
            abs(line.get('amount_currency')) or
            -abs(line.get('amount_currency')),
            'currency_id': line.get('currency_id'),
            'tax_line_id': line.get('tax_line_id'),
            'ref': line.get('ref'),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id'),
            'product_uom_id': line.get('uom_id'),
            'analytic_account_id': line.get('analytic_account_id'),
        }

    @api.multi
    def _move_line_get(self):
        account_move = []
        for sheet in self:
            val_prod = sheet.employee_id.fal_product_id
            if val_prod:
                account = val_prod.product_tmpl_id._get_product_accounts()[
                    'expense']
                if not account:
                    raise UserError(
                        _("No Expense account found for the \
                            product %s (or for it's category), \
                            please configure one.") %
                        (sheet.product_id.name))
            else:
                account = self.env['ir.property'].with_context(
                    force_company=sheet.company_id.id).get(
                    'property_account_expense_categ_id', 'product.category')
                if not account:
                    raise UserError(
                        _('Please configure Default Expense account \
                            for Product expense: \
                            `property_account_expense_categ_id`.'))
            default_price = sheet.employee_id.timesheet_cost
            if not default_price:
                default_price = sheet.employee_id.fal_product_id.\
                    product_tmpl_id.standard_price
            label = False
            for line in sheet.timesheet_ids:
                if line.name:
                    label = line.name.split('\n')[0][:64]
                else:
                    label = line.project_id.name

                val_aa = line.project_id.analytic_account_id

                move_line = {
                    'type': 'src',
                    'name': label,
                    'price_unit': val_prod.product_tmpl_id.standard_price,
                    'quantity': line.unit_amount,
                    'price': default_price * line.unit_amount,
                    'account_id': account.id,
                    'product_id': sheet.employee_id.fal_product_id.id,
                    'uom_id': val_prod.uom_id.id,
                    'analytic_account_id': val_aa.id,
                }
                account_move.append(move_line)
        return account_move

    @api.multi
    def compute_invoice_totals(self, company_currency, move_lines):
        total = 0
        total_currency = 0
        for line in move_lines:
            line['currency_id'] = False
            line['amount_currency'] = False
            line['price'] = company_currency.round(line['price'])
            total -= line['price']
            total_currency -= line['amount_currency'] or line['price']
        return total, total_currency, move_lines

    @api.multi
    def action_timesheet_draft(self):
        if self.state == 'post':
            self.write({'state': 'draft',})
        else:
            super(HrTimesheetSheet, self).action_timesheet_draft()
        if self.fal_move_id:
            self.fal_move_id.button_cancel()
        return True
