# -*- coding: utf-8 -*-
import logging
from odoo import fields, models,api, _


class res_partner(models.Model):
    _inherit = "res.partner"

    automation_followup = fields.Boolean('Automation Followup')

    @api.model
    def _execute_followup(self):
        records = self.search([('automation_followup', '=', True)])
        if records:
            self.env['account.followup.report'].execute_followup(records)
