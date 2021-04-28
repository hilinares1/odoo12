# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.addons.web_hierarchy.models.models import _HIERARCHY_TUP


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=_HIERARCHY_TUP)

    @api.model
    def _postprocess_access_rights(self, model, node):
        """ Override prost processing to add specific action access check for
        hierarchy view. """
        node = super(View, self)._postprocess_access_rights(model, node)

        if node.tag == 'hierarchy':
            Model = self.env[model]
            is_base_model = self.env.context.get('base_model_name', model) == model
            for action, operation in (('create', 'create'), ('delete', 'unlink'), ('edit', 'write')):
                if (not node.get(action) and
                        not Model.check_access_rights(operation, raise_exception=False) or
                        not self._context.get(action, True) and is_base_model):
                    node.set(action, 'false')

        return node
