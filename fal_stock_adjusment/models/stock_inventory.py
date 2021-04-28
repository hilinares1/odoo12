from odoo import models, api, fields


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    fal_planned_inventory_date = fields.Date(string="Planned Inventory Date")

    @api.multi
    def action_refresh_qty(self):
        for line in self.line_ids:
            line._compute_theoretical_qty()


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.multi
    def action_line_refresh_qty(self):
        for line in self:
            line._compute_theoretical_qty()
