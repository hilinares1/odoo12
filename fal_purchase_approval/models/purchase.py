from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            ICPSudo = self.env['ir.config_parameter'].sudo()
            if ICPSudo.get_param('fal_config_setting.fal_purc_is_proposal') and not self.user_has_groups('purchase.group_purchase_manager'):
                order.write({'state': 'to approve'})
        return super(PurchaseOrder, self).button_confirm()
