# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
import logging
_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    fal_state = fields.Selection([
        ('draft', 'Draft'),
        ('print', 'Printed'),
        ('close', 'Closed')
    ], string='Status', default='draft')
    active = fields.Boolean(default=True, help="Set active to false to hide the LOT without removing it.")
    fal_closed_date = fields.Datetime('Date Closed')

    @api.multi
    def print_stock_prod_lot(self):
        for item in self:
            item.write({'fal_state': 'print'})
        return self.env.ref('fal_serial_number_sticker.action_fal_report_lot_barcode').report_action(self)

    @api.multi
    def close_stock_prod_lot(self):
        for item in self:
            company_user = self.env.user.company_id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
            scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1).id

            name = _('Scrap') + " " + item.product_id.name + " " + item.name
            scrap_id = self.env['stock.scrap'].create({'product_id': item.product_id.id, 'product_uom_id': item.product_id.uom_id.id, 'scrap_qty': item.product_qty, 'lot_id': item.id, 'name': name, 'location_id': warehouse.lot_stock_id.id, 'scrap_location_id': scrap_location_id})
            res = scrap_id.action_validate()
            item.write({
                'fal_state': 'close',
                'active': False,
                'fal_closed_date': fields.Datetime.now(),
            })
            if scrap_id and scrap_id.name and scrap_id.id:
                self.message_post(
                    subject=_("Scrap Created"),
                    body="Scrap Record: " + scrap_id.name  + " [" + str(scrap_id.id) + "]",
                )
            if res is not True:
                return {
                    'name': _('Scrap Wizard'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'product.lot.discard',
                    'type': 'ir.actions.act_window',
                    'context': {'scrap_id': scrap_id.id, },
                    'target': 'new',
                }
            return res

    @api.multi
    def set_to_draft(self):
        for item in self:
            item.write({'fal_state': 'draft', 'active': True, })
