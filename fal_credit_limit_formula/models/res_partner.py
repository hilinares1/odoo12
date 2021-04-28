# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    fal_is_applied_credit_limit = fields.Boolean(
        string='Credit Limits', default=False)
    partner_currency_id = fields.Many2one(
        'res.currency',
        string='Credit Limit Currency')

    fal_sale_warning_type = fields.Selection(selection_add=[('percentage', 'Percentage')])
    fal_limit_restrict_margin = fields.Float(string='Restrict Margin (%)', default=10.0,
    	help="Restrict transaction on credit limit reach margin")
    fal_limit_warning_margin = fields.Float(string="Warning Margin (%)", default=20.0,
    	help="Give warning on credit limit on warning margin")
