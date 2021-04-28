# -*- coding: utf-8 -*-

import base64
import time
from odoo import models, api, _
from reportlab.graphics import barcode
from base64 import b64encode
from reportlab.graphics.barcode import createBarcodeDrawing


class ReportPickingBarcodeLabels(models.AbstractModel):
    _name = 'report.picking_barcode_report.report_picking_barcode_labels'

    @api.multi
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        report = self.env['ir.actions.report']._get_report_from_name('picking_barcode_report.report_picking_barcode_labels')
        docids = data['context']['active_ids']
        return {
            'doc_ids':  data['product_ids'],
            'doc_model': report.model,
            'docs': docids,
            'data': data,
            'get_barcode_value': self.get_barcode_value,
            'is_humanreadable': self.is_humanreadable,
            'barcode': self.barcode,
            'time': time,
        }

    def is_humanreadable(self, data):
        return data['form'].get('humanreadable') and 1 or 0

    def get_barcode_value(self, product, data):
        barcode_value = product[str(data['form'].get('barcode_field'))]
        return barcode_value

    def barcode(self, type, value, width, height, humanreadable, product):
        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable = humanreadable
        )
        attachment = self.env['ir.attachment'].search([('res_id','=', product.id)], limit=1)
        if not attachment:
            attachment_id = self.env['ir.attachment'].create({
                        'name': product.name,
                        'res_model': 'product.product',
                        'res_id': product.id or False,
                        'datas_fname': str(product.name) + '_' + 'attachment'
                    })
        else:
            attachment_id = attachment
        file_data = base64.encodestring(barcode_obj.asString('png'))
        attachment_id.update({'datas':file_data})
        return attachment_id
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: