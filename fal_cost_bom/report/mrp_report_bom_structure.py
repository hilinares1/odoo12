# -*- coding: utf-8 -*-

import json

from odoo import api, models, _
from odoo.tools import float_round

class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        lines = super(ReportBomStructure, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        lines['fal_bom_scrap_cost'] = lines.get('total', 0) * bom.fal_scrap_percentage/100
        return lines
        
