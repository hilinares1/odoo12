from openerp import fields, models, api


class ResLang(models.Model):
    _inherit = "res.lang"

    vat_format = fields.Integer('TIN Format', required=True, default=4)
    vat_sep = fields.Char('TIN Separator', default="|")
    iban_format = fields.Integer('IBAN Format', required=True, default=4)
    iban_sep = fields.Char('IBAN Separator', default="|")

    @api.model
    def _compute_vat_format(self, val):
        res = ''
        n = self.vat_format
        if val:
            array_res = [val[i:i + n] for i in range(0, len(val), n)]
            if self.vat_sep:
                res = self.vat_sep.join(array_res)
            else:
                res = ''.join(array_res)
        return res

    @api.model
    def _compute_iban_format(self, val):
        res = ''
        n = self.iban_format
        if val:
            array_res = [val[i:i + n] for i in range(0, len(val), n)]
            if self.iban_sep:
                res = self.iban_sep.join(array_res)
            else:
                res = ''.join(array_res)
        return res

    def _read_from_database(self, field_names, inherited_field_names=[]):
        context = dict(self.env.context)
        if not context.get('uid'):
            if 'vat_format' in field_names:
                field_names.remove('vat_format')
            if 'vat_sep' in field_names:
                field_names.remove('vat_sep')
            if 'iban_format' in field_names:
                field_names.remove('iban_format')
            if 'iban_sep' in field_names:
                field_names.remove('iban_sep')
        super(ResLang, self)._read_from_database(
            field_names, inherited_field_names)
