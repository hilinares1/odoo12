from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    fal_sales_price_option = fields.Boolean(string='Default Currency Option',
        help="Set default option for sale price currency.")


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ctx = dict(self._context)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        fal_sales_price_option = ICPSudo.get_param(
            'fal_config_setting.fal_sales_price_option')
        res.update(
            fal_sales_price_option=fal_sales_price_option,
        )
        ctx.update({'fal_sales_price_option': True})
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param(
            "fal_config_setting.fal_sales_price_option",
            self.fal_sales_price_option)
        return res
