from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_company_share_analytic = fields.Boolean(string='Share analytic account to all companies',
        help="Share your analytic account to all companies defined in your instance.\n"
             " * Checked : analytic account are visible for every companies, even if a company is defined on the analytic account.\n"
             " * Unchecked : Each company can see only its analytic account (analytic account where company is defined). analytic account not related to a company are visible for all companies.")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            fal_company_share_analytic=not self.env.ref(
                'analytic.analytic_comp_rule').active,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('analytic.analytic_comp_rule').write({
            'active': not self.fal_company_share_analytic})
        self.env.ref('analytic.analytic_line_comp_rule').write({
            'active': not self.fal_company_share_analytic})
