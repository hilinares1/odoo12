from odoo import models, fields


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    fal_title = fields.Char(string="Title", help="Title of the Subscription")
    fal_attachment = fields.Binary(string='Customer Invoice Attachment')
    fal_attachment_name = fields.Char(string='Attachment name')
