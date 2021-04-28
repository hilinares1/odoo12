from odoo import models, api, fields


class FalProductionOrder(models.Model):
    _inherit = 'fal.production.order'

    fal_requested_date = fields.Datetime(related="fal_sale_order_id.commitment_date", string="Commitment Date", store=True)
