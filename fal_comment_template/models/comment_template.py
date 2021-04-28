# -*- coding: utf-8 -*-
from odoo import fields, models


class FalCommentTemplate(models.Model):
    _name = 'fal.comment.template'
    _description = "Comment Template"

    name = fields.Char(
        'Name', copy=False, default='New', required=True, translate=True
    )
    active = fields.Boolean(default=True, help="The active field allows you to hide the template without removing it.")


class FalCommentLine(models.Model):
    _name = 'fal.comment.line'
    _description = "Comment Line"

    value = fields.Char(string='Value')
    fal_comment_template_id = fields.Many2one(
        'fal.comment.template', string='Template')
