# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    fal_workcenter_ids = fields.Many2many('mrp.workcenter', 'order_ids', string='Allowed Workcenters')
