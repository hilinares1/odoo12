from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.one
    @api.depends('vat')
    def _compute_fal_tin_display(self):
        tin1 = ''
        tin2 = ''
        tin3 = ''
        tin4 = ''
        if self.vat:
            if self.vat[:2]:
                tin1 = self.vat[:2]
            if self.vat[2:6]:
                tin2 = self.vat[2:6]
            if self.vat[6:9]:
                tin3 = self.vat[6:9]
            if self.vat[9:]:
                tin4 = self.vat[9:]
            self.fal_tin_display = tin1 + ' ' + tin2 + '.' + tin3 + '.' + tin4
        else:
            self.fal_tin_display = self.vat
    fal_tin_display = fields.Char(
        string="TIN Display", compute="_compute_fal_tin_display")


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    _rec_name = "fal_iban_display"

    @api.one
    @api.depends('acc_number')
    def _compute_fal_iban_display(self):
        user_lang = self.env['res.users'].browse(self.env.uid).partner_id.lang
        lang_id = self.env['res.lang'].search([('code', '=', user_lang)])
        if lang_id:
            lang_id = lang_id[0]
            self.fal_iban_display = lang_id._compute_vat_format(
                self.acc_number)

    fal_iban_display = fields.Char(
        string="IBAN Display", compute="_compute_fal_iban_display")


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.one
    @api.depends('vat')
    def _compute_fal_tin_display(self):
        tin1 = ''
        tin2 = ''
        tin3 = ''
        tin4 = ''
        if self.vat:
            if self.vat[:2]:
                tin1 = self.vat[:2]
            if self.vat[2:6]:
                tin2 = self.vat[2:6]
            if self.vat[6:9]:
                tin3 = self.vat[6:9]
            if self.vat[9:]:
                tin4 = self.vat[9:]
            self.fal_tin_display = tin1 + ' ' + tin2 + '.' + tin3 + '.' + tin4
        else:
            self.fal_tin_display = self.vat
    fal_tin_display = fields.Char(
        string="TIN Display", compute="_compute_fal_tin_display")
