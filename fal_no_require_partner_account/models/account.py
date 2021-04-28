from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_account_data(self):
        PropertyObj = self.env['ir.property']
        company = self.env['res.company']._company_default_get(
            'res.config.settings')
        todo_list = [
            ('property_account_payable_id', 'res.partner', 'account.account'),
            ('property_account_receivable_id', 'res.partner', 'account.account'),
        ]
        for record in todo_list:
            field = self.env['ir.model.fields'].search([
                ('name', '=', record[0]), ('model', '=', record[1]),
                ('relation', '=', record[2])], limit=1)
            properties = PropertyObj.search([
                ('name', '=', record[0]),
                ('company_id', '=', company.id),
                ('fields_id', '=', field.id),
                ('res_id', '=', False)])

            if properties:
                if record[0] == 'property_account_payable_id':
                    if properties[0].value_reference:
                        nums = properties[0].value_reference.split(',')
                        if self.property_account_payable_id_setting:
                            properties.write(
                                {'value_reference': str(
                                    nums[0] + ',' + str(
                                        self.property_account_payable_id_setting.id))})
                elif record[0] == 'property_account_receivable_id':
                    if properties[0].value_reference:
                        nums = properties[0].value_reference.split(',')
                        if self.property_account_receivable_id_setting:
                            properties.write(
                                {'value_reference': str(
                                    nums[0] + ',' + str(
                                        self.property_account_receivable_id_setting.id
                                    ))})
            else:
                fields = False
                if record[0] == 'property_account_receivable_id':
                    fields = self.property_account_receivable_id_setting.id
                elif record[0] == 'property_account_payable_id':
                    fields = self.property_account_payable_id_setting.id
                value = record[0] and 'account.account,' + str(fields) or False
                vals = {
                    'name': record[0],
                    'company_id': company.id,
                    'fields_id': field.id,
                    'value': value,
                }
                PropertyObj.create(vals)

    def execute(self):
        res = super(ResConfigSettings, self).execute()
        self._get_account_data()
        return res

    property_account_payable_id_setting = fields.Many2one(
        'account.account', string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]")
    property_account_receivable_id_setting = fields.Many2one(
        'account.account', string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        property_account_payable_id_setting = ICPSudo.get_param(
            'fal_no_require_partner_account.property_account_payable_id_setting')

        property_account_receivable_id_setting = ICPSudo.get_param(
            'fal_no_require_partner_account.property_account_receivable_id_setting')

        res.update(
            property_account_payable_id_setting=int(property_account_payable_id_setting),
            property_account_receivable_id_setting=int(property_account_receivable_id_setting),
        )
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "fal_no_require_partner_account.property_account_receivable_id_setting",
            self.property_account_receivable_id_setting.id)
        ICPSudo.set_param(
            "fal_no_require_partner_account.property_account_payable_id_setting",
            self.property_account_payable_id_setting.id)
        return res
