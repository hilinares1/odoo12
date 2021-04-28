# -*- coding:utf-8 -*-
from odoo import fields, models, api


class LearningResource(models.Model):
    _name = 'fal.learning.resource'
    _inherit = ['mail.thread']
    _description = 'Learning Material'

    name = fields.Char(
        string='Name', required=1, track_visibility='onchange')
    fal_number = fields.Char(string='Number', copy=False)
    fal_description = fields.Text(
        string='Description',
        size=128,
        compute='get_desc',
    )
    fal_tags = fields.Many2many('fal.learning.tag', string='Tags')
    fal_scope = fields.Many2one(
        'fal.learning.scope', string='Scope', track_visibility='onchange')
    fal_responsible = fields.Many2one(
        'res.users',
        string='Author',
        default=lambda self: self.env.user,
        track_visibility='onchange'
    )
    fal_attachment_ids = fields.Many2many(
        'ir.attachment', 'attachment_id',
        string='Attachments',
        track_visibility='onchange'
    )
    fal_description_2 = fields.Text(
        string='Description',
        size=128, track_visibility='onchange'
    )

    user_ids = fields.Many2many(
        'res.users', 'fal_user_learning_rel',
        'learning_id', 'user_id', string='Allowed Users',
        help='If empty, this material will be visible to all users.'
    )
    # command out by sandi 02-10-2018 (depends on same field)
    # @api.depends('fal_description', 'fal_description_2')
    @api.depends('fal_description_2')
    def get_desc(self):
        for line in self:
            line.fal_description = line.fal_description_2

    @api.model
    def create(self, vals):
        if vals.get('fal_number', 'New') == 'New':
            vals['fal_number'] = self.env['ir.sequence'].\
                next_by_code('fal.learning.resource') or 'New'
        return super(LearningResource, self).create(vals)


class LearningTag(models.Model):
    _name = 'fal.learning.tag'
    _description = "Learning Tag"

    name = fields.Char(
        string='Learning Tag',
        index=True,
        required=True,
        track_visibility='onchange'
    )
    code = fields.Char(
        string='Code',
        index=True,
        track_visibility='onchange'
    )


class LearningScope(models.Model):
    _name = 'fal.learning.scope'
    _description = "Learning Tag"

    name = fields.Char(
        string='Learning Scope',
        index=True,
        required=True,
        track_visibility='onchange'
    )
    code = fields.Char(
        string='Code',
        index=True,
        track_visibility='onchange'
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
