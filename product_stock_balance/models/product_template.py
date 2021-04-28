# -*- coding: utf-8 -*-

import base64
import logging
import tempfile

from odoo import _, api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.warning("Cannot import xlsxwriter")
    xlsxwriter = False


class product_template(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _compute_location_ids(self):
        """
        Compute method for location_ids - as all internal locations

        Extra info:
         * To show only viable location (with positive inventories) we filter locations already in js
         * We should include inactive locations, since configurable inputs are deactivated
         * No restrictionon company_id, since it managed by security rules
        """
        for product_id in self:
            location_ids = self.env["stock.location"].search([
                ('usage', '=', 'internal'),
                "|",
                    ("active", "=", True),
                    ("active", "=", False),
            ])
            product_id.location_ids = [(6, 0, location_ids.ids)]

    @api.multi
    def _inverse_location_ids(self):
        """
        Inverse method for location_ids: dummy method so that we can edit vouchers and save changes
        """
        return True

    location_ids = fields.One2many(
        'stock.location',
        compute=_compute_location_ids,
        inverse=_inverse_location_ids,
        string='Locations',
    )

    @api.multi
    def action_prepare_xlsx_balance(self):
        """
        The method to make .xlsx table of stock balances

        1. Prepare workbook and styles
        2. Prepare header row
          2.1 Get column name like 'A' or 'S' (ascii char depends on counter)
        3. Prepare each row of locations
        4. Create an attachment

        Returns:
         * action of downloading the xlsx table

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        if not xlsxwriter:
            raise UserError(_("The Python library xlsxwriter is installed. Contact your system administrator"))
        # 1
        file_path = tempfile.mktemp(suffix='.xlsx')
        workbook = xlsxwriter.Workbook(file_path)
        styles = {
            'main_header_style': workbook.add_format({
                'bold': True,
                'font_size': 11,
                'border': 1,
            }),
            'main_data_style': workbook.add_format({
                'font_size': 11,
                'border': 1,
            }),
        }
        worksheet = workbook.add_worksheet(u"{}#{}.xlsx".format(self.name, fields.Date.today()))
        # 2
        cur_column = 0
        for column in [_("Location"), _("On Hand"), _("Forecast"), _("Incom"), _("Out")]:
            worksheet.write(0, cur_column, column, styles.get("main_header_style"))
            # 2.1
            col_letter = chr(cur_column + 97).upper()
            column_width = cur_column == 0 and 60 or 8
            worksheet.set_column('{c}:{c}'.format(c=col_letter), column_width)
            cur_column += 1
        # 3
        elements = []
        for loc in self.location_ids:
            balances = loc._return_balances()
            if balances:
                elements.append({
                    "name": loc.name,
                    "id": loc.id,
                    "qty_available": balances.get("qty_available"),
                    "incoming_qty": balances.get("incoming_qty"),
                    "outgoing_qty": balances.get("outgoing_qty"),
                    "virtual_available": balances.get("virtual_available"),
                })
        elements = self.env["stock.location"].prepare_elements_for_hierarchy(args={"elements": elements})
        row = 1
        for loc in elements:
            spaces = ""
            level = loc.get("level")
            itera = 0
            while itera != level:
                spaces += "    "
                itera += 1
            instance = (
                spaces + loc.get("name"),
                loc.get("qty_available"),
                loc.get("virtual_available"),
                loc.get("incoming_qty"),
                loc.get("outgoing_qty"),
            )
            for counter, column in enumerate(instance):
                value = column
                worksheet.write(
                    row,
                    counter,
                    value,
                    styles.get("main_data_style")
                )
            row += 1
        workbook.close()
        # 4
        with open(file_path, 'rb') as r:
            xls_file = base64.b64encode(r.read())
        att_vals = {
            'name':  u"{}#{}.xlsx".format(self.name, fields.Date.today()),
            'type': 'binary',
            'datas': xls_file,
            'datas_fname': u"{}#{}.xlsx".format(self.name, fields.Date.today()),
        }
        attachment_id = self.env['ir.attachment'].create(att_vals)
        self.env.cr.commit()
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web/content/{}?download=true'.format(attachment_id.id,),
            'target': 'self',
        }
        return action
