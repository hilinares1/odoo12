# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import float_is_zero
from dateutil.relativedelta import relativedelta


class AccountReport(models.AbstractModel):
    _inherit = 'account.financial.html.report'

    filter_groupby = True

    @api.model
    def _get_options(self, previous_options=None):
        if self.filter_groupby:
            self.filter_groupby_ids = []
        return super(AccountReport, self)._get_options(previous_options)

    def _set_context(self, options):
        ctx = super(AccountReport, self)._set_context(options)
        if options.get('groupby_ids'):
            ctx['groupby_ids'] = self.env['ir.model.fields'].browse([int(field) for field in options['groupby_ids']])
        return ctx

    def get_report_informations(self, options):
        res = super(AccountReport, self).get_report_informations(options)
        options = self._get_options(options)
        searchview_dict = {'options': options, 'context': self.env.context}
        template_no_values = self.env['ir.ui.view'].render_template('fal_account_report_groupby.search_template_groupby', values=searchview_dict)
        if options.get('groupby'):
            model = self.env['ir.model'].search([('model', '=', 'account.move.line')])
            searchview_dict['move_line_fields'] = [(field.id, field.name) for field in model.field_id.filtered(lambda l: l.ttype in ['many2one', 'selection'])] or False
            res['options']['selected_groupby_ids'] = [self.env['ir.model.fields'].browse(int(field)).name for field in options['groupby_ids']]
            template_with_values = self.env['ir.ui.view'].render_template('fal_account_report_groupby.search_template_groupby', values=searchview_dict)
            res['searchview_html'] = res['searchview_html'].replace(template_no_values, template_with_values)
        return res

    def fal_set_groupby(self, field):
        for item in self:
            for report in item.line_ids:
                parent_child = [
                    '|',
                    ('id', 'child_of', report.id),
                    ('id', 'parent_of', report.id),
                ]
                line = report.search(parent_child)
                report_line = line.filtered(lambda a: a.groupby)
                new_field = self.env['ir.model.fields'].browse(int(field))
                for item in report_line:
                    item.sudo().write({'groupby': new_field.name})
