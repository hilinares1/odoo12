from odoo import models, fields


class IrModel(models.Model):
    _inherit = 'ir.model'

    fal_allow_external_message = fields.Boolean(
        string="Allow External Message", default=True
    )
