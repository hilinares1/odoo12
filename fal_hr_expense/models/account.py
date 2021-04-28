# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    expense_journal = fields.Boolean(
        help="Specify whether the journal can be selected in an HR expense.",
        string="Expense Journal")
