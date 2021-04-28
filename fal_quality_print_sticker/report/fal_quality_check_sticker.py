from odoo import models, api
try:
    import qrcode
except ImportError:
    qrcode = None
import base64
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


class FalInternationalQualityCheckSticker(models.AbstractModel):
    _name = 'report.fal_quality_print_sticker.inter_quality_check_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['quality.check'].browse(docids)
        temp = []
        for quality in docs:
            if quality.product_id.categ_id.isfal_finished_product:
                for x in xrange(int(quality.fal_total_qty_to_check)):
                    temp_qr_code = ""
                    if quality.company_id.fal_producer_name_sticker:
                        temp_qr_code += "1. Producer: " + str(quality.company_id.fal_producer_name_sticker.encode('utf-8', 'ignore'))
                    temp_qr_code += "\n" + str(quality.company_id.phone.encode('utf-8', 'ignore'))
                    temp_qr_code += "\n2. Batch quantity: " + str(quality.fal_total_qty_to_check)
                    temp_qr_code += "\n3. Production date: " + str(quality.fal_production_order_id.create_date)
                    temp_qr_code += "\n4. Delivery date: " + str(quality.fal_production_order_id.delivery_planned_date)
                    temp_qr_code += "\n" + str(quality.company_id.fal_website_sticker)

                    temp.append({
                        'fal_header_sticker':
                            quality.company_id.fal_header_sticker,
                        'fal_description_sticker_1':
                            quality.company_id.fal_description_sticker_1,
                        'fal_description_sticker_2':
                            quality.company_id.fal_description_sticker_2,
                        'fal_of_number':
                            quality.fal_production_order_id.name or
                            ' ',
                        'fal_sale_ref':
                            quality.product_id.name,
                        'fal_company_id':
                            quality.company_id,
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
        docs = self.env['quality.check'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'quality.check',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
            '_get_logo': self._get_logo,
            '_get_qr_code': self._get_qr_code,
        }
        return docargs


class FalQualityCheckSticker(models.AbstractModel):
    _name = 'report.fal_quality_print_sticker.quality_check_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['quality.check'].browse(docids)
        temp = []
        for quality in docs:
            if quality.product_id.categ_id.isfal_finished_product:
                for x in xrange(int(quality.fal_total_qty_to_check)):
                    temp.append({
                        'fal_header_sticker':
                            quality.company_id.fal_header_sticker,
                        'fal_description_sticker_1':
                            quality.company_id.fal_description_sticker_1,
                        'fal_description_sticker_2':
                            quality.company_id.fal_description_sticker_2,
                        'fal_of_number':
                            quality.fal_production_order_id.name or
                            ' ',
                        'fal_sale_ref':
                            quality.product_id.name, })
        return temp

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['quality.check'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'quality.check',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
        }
        return docargs


# new
class FalNewInternationalStickerQuality(models.AbstractModel):
    _name = 'report.fal_quality_print_sticker.new_inter_sticker_quality'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['quality.check'].browse(docids)
        temp = []
        for quality in docs:
            if quality.product_id.categ_id.isfal_finished_product:
                for x in xrange(int(quality.fal_total_qty_to_check)):
                    temp.append({
                        'fal_header_sticker': quality.company_id.fal_header_sticker,
                        'fal_of_number': quality.fal_production_order_id.name or ' ',
                        'fal_sale_ref': quality.product_id.name or '',
                        'fal_company_id': quality.company_id,
                    })
        return temp

    @api.model
    def _get_logo(self, company_id):
        company_obj = self.env['res.company']
        company_id = company_obj.browse(company_id)
        _logger.info("__xxx__")
        _logger.info(company_id.fal_logo_sticker)
        if company_id.fal_logo_sticker:
            return company_id.fal_logo_sticker
        else:
            return False

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['quality.check'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'quality.check',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
            '_get_logo': self._get_logo,
        }
        return docargs


class OldFalQualityCheckSticker(models.AbstractModel):
    _name = 'report.fal_quality_print_sticker.old_quality_check_sticker'

    @api.model
    def _get_line_temp(self, docids):
        docs = self.env['quality.check'].browse(docids)
        temp = []
        for quality in docs:
            if quality.product_id.categ_id.isfal_finished_product:
                for x in xrange(int(quality.fal_total_qty_to_check)):
                    temp.append({
                        'fal_header_sticker':
                            quality.company_id.fal_header_sticker,
                        'fal_description_sticker_1':
                            quality.company_id.fal_description_sticker_1,
                        'fal_description_sticker_2':
                            quality.company_id.fal_description_sticker_2,
                        'fal_of_number':
                            quality.fal_production_order_id.name or
                            ' ',
                        'fal_sale_ref':
                            quality.product_id.name, })
        return temp

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['quality.check'].browse(docids)
        self._get_line_temp(docids=docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'quality.check',
            'docs': docs,
            '_get_line_temp': self._get_line_temp,
        }
        return docargs
