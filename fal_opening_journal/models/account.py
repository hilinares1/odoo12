# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_netting = fields.Boolean(string='Is Partner Netting',
        required=True, default=False)
    