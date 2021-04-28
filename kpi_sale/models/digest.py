# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_all_sale_time_delta_average = fields.Boolean('All Sales Time Average')
    kpi_all_sale_time_delta_average_value = fields.Float(compute='_compute_kpi_all_sale_time_delta_average_value')

    def _compute_kpi_all_sale_time_delta_average_value(self):
        if not self.env.user.has_group('sales_team.group_sale_salesman_all_leads'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))
        for record in self:
            start, end, company = record._get_kpi_compute_parameters()
            all_channels_sales = self.env['sale.report'].read_group(
                [
                    ('confirmation_date', '>=', start),
                    ('confirmation_date', '<', end),
                    ('company_id', '=', company.id),
                    ('state', '=', 'sale'),
                ], ['confirmation_delay_second'], ['confirmation_delay_second'])

            delta = 0.
            if all_channels_sales:
                delta = sum([channel_sale['confirmation_delay_second'] for channel_sale in all_channels_sales]) / len(
                    all_channels_sales)

            # convert and save
            record.kpi_all_sale_time_delta_average_value = delta

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res['kpi_all_sale_time_delta_average'] = 'sale.report_all_channels_sales_action&menu_id=%s' % self.env.ref(
            'sale.sale_menu_root').id
        return res
