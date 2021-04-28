# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    confirmation_delay_second = fields.Float('Delay second', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        res = super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
        result = ""
        key = "delay,"
        new_value = "\n            extract(epoch from avg(s.confirmation_date-s.create_date))::decimal(16,2) as " \
                    "confirmation_delay_second,"
        new_value_2 = "\n            extract(epoch from avg(pos.date_order-pos.create_date))::decimal(16,2) as " \
                      "confirmation_delay_second,"
        lst_res = res.split(key)
        if len(lst_res) <= 1:
            raise Exception("The SQL query is not supported, please contact your sysadmin.")

        if len(lst_res) > 1:
            result = lst_res[0]
            result += key
            result += new_value
            result += lst_res[1]

        if len(lst_res) > 2:
            result += key
            result += new_value_2
            result += lst_res[2]

        if len(lst_res) > 3:
            raise Exception("The SQL query is not supported, please contact your sysadmin.")

        return result
