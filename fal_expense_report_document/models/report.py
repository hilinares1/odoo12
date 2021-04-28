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


class FalInternationalPickingSticker(models.AbstractModel):
    _name = 'report.fal_expense_report_document.fal_expense_report_document'

    @api.model
    def _get_line_temp(self, docids):
        temp = []
        for docid in docids:
            doc = self.env['hr.expense.sheet'].browse(docid)
            res = self.env['ir.attachment'].search([('res_model', '=', 'hr.expense'), ('res_id', 'in', doc.expense_line_ids.ids)])
            temp.append({
                'attachment': res,
            })
        return temp

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['hr.expense.sheet'].browse(docids)
        docargs = {
            'doc_ids': docs.ids,
            'doc_model': 'hr.expense.sheet',
            'docs': docs,
            '_get_line_temp': self._get_line_temp(docids),
        }
        return docargs
