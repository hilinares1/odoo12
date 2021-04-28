from odoo import models, api
try:
    import qrcode
except ImportError:
    qrcode = None
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


class FalInternationalPickingSticker(models.AbstractModel):
    _name = 'report.fal_print_sticker.international_picking_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['stock.picking'].browse(docids)
        temp = []
        for picking in docs:
            for move in picking.move_lines:
                if move.product_id.categ_id.isfal_finished_product:
                    for x in xrange(int(move.product_uom_qty)):
                        temp_qr_code = ""
                        temp_qr_code += "1. Producer: " + str(move.company_id.fal_producer_name_sticker)
                        temp_qr_code += "\n" + str(move.company_id.phone)
                        temp_qr_code += "\n2. Batch quantity: " + str(move.product_uom_qty)
                        temp_qr_code += "\n3. Production date: " + str(move.production_id.fal_prod_order_id.create_date)
                        temp_qr_code += "\n4. Delivery date: " + str(move.production_id.fal_prod_order_id.delivery_planned_date)
                        temp_qr_code += "\n" + str(move.company_id.fal_website_sticker)

                        temp.append({
                            'fal_header_sticker':
                                move.company_id.fal_header_sticker,
                            'fal_description_sticker_1':
                                move.company_id.fal_description_sticker_1,
                            'fal_description_sticker_2':
                                move.company_id.fal_description_sticker_2,
                            'fal_of_number': move.fal_of_number or ' ',
                            'fal_sale_ref': move.name,
                            'fal_company_id': move.company_id,
                            'fal_qr_code': self._get_qr_code(temp_qr_code)})
        return temp

    @api.model
    def _get_logo(self, company_id):
        company_obj = self.env['res.company']
        company_id = company_obj.browse(company_id)
        if company_id.fal_logo_sticker:
            return company_id.fal_logo_sticker
        else:
            return False

    @api.model
    def _get_qr_code(self, data):
        stream = BytesIO()
        if qrcode is None:
            return base64.b64encode(stream.getvalue())
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.seek(0)
        img.save(stream, format="jpeg")
        return base64.b64encode(stream.getvalue())

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
            '_get_logo': self._get_logo,
            '_get_qr_code': self._get_qr_code,
        }
        return docargs


class FalPrintSticker(models.AbstractModel):
    _name = 'report.fal_print_sticker.picking_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['stock.picking'].browse(docids)
        temp = []
        for picking in docs:
            for move in picking.move_lines:
                if move.product_id.categ_id.isfal_finished_product:
                    for x in xrange(int(move.product_uom_qty)):
                        temp.append({
                            'fal_header_sticker':
                                move.company_id.fal_header_sticker,
                            'fal_description_sticker_1':
                                move.company_id.fal_description_sticker_1,
                            'fal_description_sticker_2':
                                move.company_id.fal_description_sticker_2,
                            'fal_of_number':
                                move.fal_of_number or ' ',
                            'fal_sale_ref': move.name,
                        })
        return temp

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
        }
        return docargs


class FalNewInternationalStickerPicking(models.AbstractModel):
    _name = 'report.fal_print_sticker.new_international_sticker_picking'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['stock.picking'].browse(docids)
        temp = []
        for picking in docs:
            for move in picking.move_lines:
                if move.product_id.categ_id.isfal_finished_product:
                    for x in xrange(int(move.product_uom_qty)):
                        temp.append({
                            'fal_header_sticker': move.company_id.fal_header_sticker,
                            'fal_of_number': move.fal_of_number or ' ',
                            'fal_sale_ref': move.sale_line_id.name or '',
                            'fal_company_id': move.company_id,
                        })
        return temp

    @api.model
    def _get_logo(self, company_id):
        company_obj = self.env['res.company']
        company_id = company_obj.browse(company_id)
        if company_id.fal_logo_sticker:
            return company_id.fal_logo_sticker
        else:
            return False

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
            '_get_logo': self._get_logo,
        }
        return docargs


class OldFalPrintSticker(models.AbstractModel):
    _name = 'report.fal_print_sticker.old_picking_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['stock.picking'].browse(docids)
        temp = []
        for picking in docs:
            for move in picking.move_lines:
                if move.product_id.categ_id.isfal_finished_product:
                    for x in xrange(int(move.product_uom_qty)):
                        temp.append({
                            'fal_header_sticker':
                                move.company_id.fal_header_sticker,
                            'fal_description_sticker_1':
                                move.company_id.fal_description_sticker_1,
                            'fal_description_sticker_2':
                                move.company_id.fal_description_sticker_2,
                            'fal_of_number':
                                move.fal_of_number or ' ',
                            'fal_sale_ref': move.name,
                        })
        return temp

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
        }
        return docargs
