# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    fal_procurement_alias_prefix = fields.Char('Default Alias Name for Procurement')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            fal_procurement_alias_prefix=self.env.ref('fal_procurement_email.mail_alias_procurement').alias_name,
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env.ref('fal_procurement_email.mail_alias_procurement').write({'alias_name': self.fal_procurement_alias_prefix})
