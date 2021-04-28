# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    fal_name = fields.Char(string='Product Name', related='product_id.name')

    fal_component_product = fields.Char(
        string='Component Product',
        related='product_id.bom_ids.bom_line_ids.product_id.name'
    )
