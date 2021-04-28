# -*- coding: utf-8 -*-

from odoo import fields, models


class FalCommentTemplate(models.Model):
    _inherit = "fal.comment.template"

    tax_ids = fields.Many2many('account.tax', string='Tax')
