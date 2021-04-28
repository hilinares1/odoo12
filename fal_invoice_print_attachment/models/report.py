# -*- coding: utf-8 -*-
# © 2015 Gael Rabier, Pierre Faniel, Jérôme Guerriat
# © 2015 Niboo SPRL (<https://www.niboo.be/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import base64
import logging
import os
import tempfile

import io
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval as eval
from PyPDF2 import PdfFileWriter, PdfFileReader

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.multi
    def render_qweb_pdf(self, res_ids=None, data=None):
        if self == self.env.ref('fal_invoice_print_attachment.report_invoice_vendor_bill'):
            if len(res_ids) > 1:
                temporary_files = []
                for docid in res_ids:
                    report_pdf = super(IrActionsReport, self).render_qweb_pdf(
                        docid, data)
                    pdf_incl_terms = self.add_attachment(
                        docid, report_pdf)

                    pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                        suffix='.pdf', prefix='report.tmp.')
                    os.write(pdfreport_fd, pdf_incl_terms[0])
                    os.close(pdfreport_fd)

                    temporary_files.append(pdfreport_path)

                pdf_writer = PdfFileWriter()
                for path in temporary_files:
                    pdf_reader = PdfFileReader(path)
                    for page in range(pdf_reader.getNumPages()):
                        pdf_writer.addPage(pdf_reader.getPage(page))
                stream_to_write = io.BytesIO()
                pdf_writer.write(stream_to_write)

                pdf_content = stream_to_write.getvalue()
                for temporary_file in temporary_files:
                    try:
                        os.unlink(temporary_file)
                    except (OSError, IOError):
                        _logger.error(
                            'Error when trying to remove file %s'
                            % temporary_file)
                return pdf_content, 'pdf'
            else:
                report_pdf = super(IrActionsReport, self).render_qweb_pdf(
                    res_ids, data)
                return self.add_attachment(res_ids, report_pdf)
        else:
            return super(IrActionsReport, self).render_qweb_pdf(res_ids, data)

    @api.model
    def add_attachment(self, res_id, original_report_pdf):
        model = self.model
        object = self.env[model].browse(res_id)
        company = object.company_id
        if not object.fal_attachment:
            return original_report_pdf

        attachment_decoded = base64.b64decode(object.fal_attachment)

        if attachment_decoded:
            writer = PdfFileWriter()
            stream_original_report = io.BytesIO(original_report_pdf[0])
            reader_original_report = PdfFileReader(stream_original_report)
            stream_attachment = io.BytesIO(
                attachment_decoded)
            reader_attachment = PdfFileReader(
                stream_attachment)
            for page in range(0, reader_original_report.getNumPages()):
                writer.addPage(reader_original_report.getPage(page))

            for page in range(0, reader_attachment.getNumPages()):
                writer.addPage(reader_attachment.getPage(page))

            stream_to_write = io.BytesIO()
            writer.write(stream_to_write)

            combined_pdf = stream_to_write.getvalue()
            return combined_pdf, 'pdf'
        else:
            return original_report_pdf
