from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    fal_shortname = fields.Char(
        "Short name", index=True, related="partner_id.fal_shortname")

    @api.multi
    def name_get(self):
        res = super(ResCompany, self).name_get()
        for index, company in enumerate(res, start=0):
            company_obj = self.browse(company[0])
            company = (company[0], company_obj.fal_shortname or company_obj.name)
            res[index] = company
        return res