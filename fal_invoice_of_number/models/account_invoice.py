from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    fal_of_number = fields.Char(
        string="PO Number",
        size=128,
        store=True,
    )

    fal_of_number_id = fields.Many2one(
        'fal.production.order',
        string='PO Number',
    )
