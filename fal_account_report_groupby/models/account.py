# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountReport(models.AbstractModel):
    _inherit = 'account.move.line'

    fal_consolidation_id = fields.Many2one(
        'account.account',
        'Consolidation Account',
        related="account_id.fal_consolidation_id", store=True)
