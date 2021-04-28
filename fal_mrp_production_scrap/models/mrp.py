from odoo import models, api, fields


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    fal_scrap_percentage = fields.Float(string='Scrap Percentage')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fal_scrap_percentage = fields.Float(string='Scrap Percentage')

    @api.onchange('bom_id')
    def onchange_bom_id_fal(self):
        if self.bom_id:
            self.fal_scrap_percentage = self.bom_id.fal_scrap_percentage


class FalProductionOrder(models.Model):
    _inherit = 'fal.production.order'

    scrap_percentage = fields.Float(
        string='Scrap Percentage',
    )

    qty_to_transfer = fields.Float(
        string='Qty to Transfer',
    )

    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        res = super(FalProductionOrder, self).onchange_product_id()
        if self.product_id:
            self.scrap_percentage = self.bom_id.fal_scrap_percentage

        return res

    @api.onchange('scrap_percentage', 'qty_to_transfer')
    def onchange_qty_to_transfer(self):
        self.qty_to_produce = self.qty_to_transfer / \
            (1 - self.scrap_percentage / 100.0)

    @api.model
    def _prepare_mo_vals(self, bom):
        res = super(FalProductionOrder, self)._prepare_mo_vals(bom)
        res['fal_scrap_percentage'] = self.scrap_percentage
        return res
