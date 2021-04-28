from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_stock_picking_name_concatenated(self):
        stock_picking_name = ''
        for stock_picking in self.picking_ids:
            if stock_picking.state == 'done':
                stock_picking_name += stock_picking.name + ", "
        stock_picking_name = stock_picking_name[:-2]
        return stock_picking_name
