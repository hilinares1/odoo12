from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(selection_add=[
        ('lost', 'Lost'),
    ])

    def action_lost(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.lost.quotation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def fal_action_cancel(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.cancel.quotation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


class LostReason(models.Model):
    _name = 'fal.lost.reason'

    name = fields.Char(string='name')


class CancelReason(models.Model):
    _name = 'fal.cancel.reason'

    name = fields.Char(string='name')
