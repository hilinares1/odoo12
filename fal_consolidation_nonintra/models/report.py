from odoo import models, fields, api


class IrFilters(models.Model):
    _inherit = 'ir.filters'

    @api.model
    def update_non_intra_domain(self):
        non_intra = self.env.ref('fal_consolidation_nonintra.filters_non_intra')
        non_intra._set_partner_company_domain()

    def _set_partner_company_domain(self):
        company = self.env['res.company'].search([])
        domain = [('partner_id', 'not in', tuple(c.partner_id.id for c in company))]
        self.write({'domain': domain})


class AccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    fal_non_intra = fields.Boolean(string='Non Intra Filters')

    @api.onchange('fal_non_intra')
    def _onchange_non_intra(self):
        filters = self.applicable_filters_ids.ids
        non_intra = self.env.ref('fal_consolidation_nonintra.filters_non_intra')
        if self.fal_non_intra:
            filters.append(non_intra.id)
        else:
            if non_intra.id in filters:
                filters.remove(non_intra.id)
        # to refresh domain if there is any change
        non_intra._set_partner_company_domain()
        self.applicable_filters_ids = [(6, 0, filters)]

    @api.onchange('applicable_filters_ids')
    def _onchange_applicable_filters_ids(self):
        non_intra = self.env.ref('fal_consolidation_nonintra.filters_non_intra')
        self.fal_non_intra = non_intra in self.applicable_filters_ids
