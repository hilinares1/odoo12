from odoo import models, api


class FalProductionOrder(models.Model):
    _inherit = 'fal.production.order'

    @api.model
    def _prepare_mo_vals(self, bom):
        res = super(FalProductionOrder, self)._prepare_mo_vals(bom)
        if self.fal_sale_order_id:
            res['project_id'] = self.fal_sale_order_id.analytic_account_id.id
        return res
