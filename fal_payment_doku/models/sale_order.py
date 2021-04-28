# coding: utf-8
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    doku_so_difference_amount = fields.Float(string='Doku Difference Amount', compute='_compute_so_difference_amount', store=True)

    @api.multi
    @api.depends('amount_total')
    def _compute_so_difference_amount(self):
        for record in self:
            check_margin_amount = round(
                record.amount_total) - record.amount_total
            record.doku_so_difference_amount = check_margin_amount
