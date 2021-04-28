from odoo import fields, models, api
from odoo.osv import expression


class AccountAccount(models.Model):
    _inherit = "account.account"
    _order = "sequence, code"

    def _get_fal_standard_code(self):
        start = 0
        if self.code and self.name:
            if self.code and self.code.find('_'):
                start = self.code.find('_')
            std_code = self.code and self.code[start + 1:]
            format = '0000000'
            std_code_format = std_code + format[len(std_code):]
            return std_code_format + ' ' + self.name
        else:
            return ''

    sequence = fields.Integer(default=10)
    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for account in self:
            account.display_name = account._get_fal_standard_code()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        res = super(AccountAccount, self).name_get()
        new_res = []
        for item in res:
            acc = self.browse(item[0])
            new_name = acc._get_fal_standard_code()
            new_res.append((item[0], new_name))
        return new_res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res = super(AccountAccount, self).name_search(
            name, args, operator, limit)
        args = args or []
        domain = []
        if name:
            domain = [
                '|', '|',
                ('code', '=ilike', name + '%'),
                ('name', operator, name),
                ('display_name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain
        res = self.search(domain + args, limit=limit)
        return res.name_get()


class AccountAnalytic(models.Model):
    _inherit = 'account.analytic.account'
    _order = 'sequence, code, name asc'

    sequence = fields.Integer(default=10)
