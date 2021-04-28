# -*- coding: utf-8 -*-
from odoo import models, fields
from datetime import datetime
from odoo.tools.misc import formatLang, format_date
from odoo.tools.translate import _
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT


class report_account_followup_report(models.AbstractModel):
    _inherit = "account.followup.report"

    def _get_columns_name(self, options):
        headers = super(
            report_account_followup_report, self)._get_columns_name(options)
        headers.insert(1, {
            'name': _(' Title '), 'class': 'date',
            'style': 'text-align:center; white-space:nowrap;'},)
        return headers

    def _get_lines(self, options, line_id=None):
        lines = super(
            report_account_followup_report, self)._get_lines(options, line_id)
        """
        Override
        Compute and return the lines of the columns of the follow-ups report.
        """
        # Get date format for the lang
        partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
        if not partner:
            return []
        lang_code = partner.lang or self.env.user.lang or 'en_US'

        lines = []
        res = {}
        today = fields.Date.today()
        line_num = 0
        for l in partner.unreconciled_aml_ids:
            if l.company_id == self.env.user.company_id:
                if self.env.context.get('print_mode') and l.blocked:
                    continue
                currency = l.currency_id or l.company_id.currency_id
                if currency not in res:
                    res[currency] = []
                res[currency].append(l)
        for currency, aml_recs in res.items():
            total = 0
            total_issued = 0
            for aml in aml_recs:
                amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
                date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
                total += not aml.blocked and amount or 0
                is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
                is_payment = aml.payment_id
                if is_overdue or is_payment:
                    total_issued += not aml.blocked and amount or 0
                if is_overdue:
                    date_due = {'name': date_due, 'class': 'color-red date', 'style': 'white-space:nowrap;text-align:center;color: red;'}
                if is_payment:
                    date_due = ''
                move_line_name = aml.invoice_id.name or aml.name
                if self.env.context.get('print_mode'):
                    move_line_name = {'name': move_line_name, 'style': 'text-align:right; white-space:normal;'}
                amount = formatLang(self.env, amount, currency_obj=currency)
                line_num += 1
                columns = [aml.invoice_id.fal_title, format_date(self.env, aml.date, lang_code=lang_code), date_due, aml.invoice_id.origin, move_line_name, aml.expected_pay_date and aml.expected_pay_date +' '+ aml.internal_note or '', {'name': aml.blocked, 'blocked': aml.blocked}, amount]
                if self.env.context.get('print_mode'):
                    columns = columns[:5] + columns[7:]
                lines.append({
                    'id': aml.id,
                    'invoice_id': aml.invoice_id.id,
                    'view_invoice_id': self.env['ir.model.data'].get_object_reference('account', 'invoice_form')[1],
                    'account_move': aml.move_id,
                    'name': aml.move_id.name,
                    'caret_options': 'followup',
                    'move_id': aml.move_id.id,
                    'type': is_payment and 'payment' or 'unreconciled_aml',
                    'unfoldable': False,
                    'has_invoice': bool(aml.invoice_id),
                    'columns': [type(v) == dict and v or {'name': v} for v in columns],
                })
            total_due = formatLang(self.env, total, currency_obj=currency)
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': 'total',
                'unfoldable': False,
                'level': 0,
                'columns': [{'name': v} for v in [''] * (4 if self.env.context.get('print_mode') else 6) + [total >= 0 and _('Total Due') or '', total_due]],
            })
            if total_issued > 0:
                total_issued = formatLang(self.env, total_issued, currency_obj=currency)
                line_num += 1
                lines.append({
                    'id': line_num,
                    'name': '',
                    'class': 'total',
                    'unfoldable': False,
                    'level': 0,
                    'columns': [{'name': v} for v in [''] * (4 if self.env.context.get('print_mode') else 6) + [_('Total Overdue'), total_issued]],
                })
            # Add an empty line after the total to make a space between two currencies
            line_num += 1
            lines.append({
                'id': line_num,
                'name': '',
                'class': '',
                'unfoldable': False,
                'level': 0,
                'columns': [],
            })
        return lines

    def get_body_html(self, options):
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        options['keep_summary'] = True
        body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang).get_html(options)    
        body = append_content_to_html(body_html, self.env.user.signature or '', plaintext=False)
        body = body.replace("<thead>", "<tbody>")
        body = body.replace("</thead>", "</tbody>")
        body = body.replace("<th>", "<td>")
        body = body.replace("</th>", "</td>")
        body = body.replace("<thead", "<tbody")
        body = body.replace("<th", "<td")
        template = self.env.ref('fal_customer_statement.email_subject_fal_customer_statement')
        template.sudo().write({'body_html': body})
        res = {
            'default_partner_ids': [partner.id],
            'default_template_id': template.id,
            'default_model' : 'account.followup.report',
        }
        return res
