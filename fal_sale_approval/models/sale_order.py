from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import RedirectWarning, UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    state = fields.Selection(selection_add=[
        ('waitingapproval', 'Wait Approval'),
    ])


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _check_proposal(self):

        if self.user_has_groups('sales_team.group_sale_manager'):
            return False
        else:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            if ICPSudo.get_param('fal_config_setting.fal_is_proposal'):
                return True
            else:
                return False

    @api.multi
    def action_propose(self):
        if self._check_proposal():
            if self.user_has_groups('sales_team.group_sale_manager'):
                self.action_confirm()
            else:
                self.action_wait()

            # keep wizard if want to show list of restriction
            # view = self.env.ref('fal_sale_approval.view_fal_sale_proposal_wizard')
            # return {
            #     'name': _('Propose Quotation?'),
            #     'type': 'ir.actions.act_window',
            #     'view_type': 'form',
            #     'view_mode': 'form',
            #     'res_model': 'fal.sale.proposal.wizard',
            #     'views': [(view.id, 'form')],
            #     'view_id': view.id,
            #     'target': 'new',
            # }
        else:
            self.action_confirm()

    state = fields.Selection(selection_add=[
        ('waitingapproval', 'Wait Approval'),
    ])

    @api.multi
    def action_wait(self):
        orders = self.filtered(lambda s: s.state in ['draft', 'sent'])
        return orders.write({
            'state': 'waitingapproval',
        })
