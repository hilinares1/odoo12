# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Users(models.Model):
    _inherit = 'res.users'

    purchase_team_id = fields.Many2one(
        'srm.team', "User's Purchases Team",
        help='Purchases Team the user is member of. Used to compute the members of a Purchases Team through the inverse one2many')
