import logging
from odoo import models, api, _, fields

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    fal_number_project = fields.Integer(compute='fal_count_project', string="Number of Project")

    @api.multi
    def fal_count_project(self):
        nbr = 0
        res = []
        for sale in self.order_ids:
            if sale.project_ids:
                for project in sale.project_ids:
                    if project.id:
                        nbr += 1
                        res.append((project.id))
        self.fal_number_project = nbr
        return {
            'name': _('Project'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'project.project',
            'views': [(self.env.ref('fal_crm_lead_project.view_project_fal_crm_lead_project').id or False, 'tree'), (self.env.ref('project.edit_project').id or False, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', res)],
        }
