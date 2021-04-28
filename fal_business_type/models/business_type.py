from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class BusinessType(models.Model):
    _name = 'fal.business.type'
    _description = 'Cluedoo business type'

    name = fields.Char(
        'Name', copy=False, default='New', required=True
    )
    fal_business_prefix = fields.Char(
        'Prefix', copy=False
    )
    fal_business_suffix = fields.Char(
        'Suffix', copy=False
    )
    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")


    @api.onchange('fal_business_prefix')
    def onchange_fal_business_prefix(self):
        pass

    @api.onchange('fal_business_suffix')
    def onchange_fal_business_suffix(self):
        pass

    @api.multi
    def launch_create_menu_wizard(self):
        view_id = self.env.ref('fal_business_type.business_create_menu_wizard_form_view').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Menu'),
            'view_mode': 'form',
            'res_model': 'create.menu.wizard',
            'target': 'new',
            'views': [[view_id, 'form']],
            'context': {'active_id': self.id},
        }
