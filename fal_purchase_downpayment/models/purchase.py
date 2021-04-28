from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_view_purchase_downpayment(self):
        view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'fal_purchase_downpayment.view_purchase_advance_payment_inv'
        )
        view = {
            'name': _('Down Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.advance.payment.inv',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'readonly': True,
            'context': self.env.context
        }
        return view

    @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
        if 'order_line' not in default:
            default['order_line'] = [(0, 0, line.copy_data()[0]) for line in self.order_line.filtered(lambda l: not l.fal_is_downpayment)]
        return super(PurchaseOrder, self).copy_data(default)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    fal_is_downpayment = fields.Boolean(string='Is Deposit Line')
