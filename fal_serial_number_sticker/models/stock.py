# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.multi
    def print_barcode(self):
        for operation in self:
            if operation.lot_id:
                return self.env.ref('fal_serial_number_sticker.action_fal_report_lot_barcode').report_action(operation.lot_id)
            else:
                raise ValidationError(_('Serial Number not Found, Please assign serial number first!!!'))
