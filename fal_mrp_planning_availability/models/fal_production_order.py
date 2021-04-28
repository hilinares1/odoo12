from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class FalProductionOrderInherit(models.Model):
    _inherit = 'fal.production.order'

    @api.multi
    def write(self, vals):
        if vals.get('is_ready', False):
            if vals['is_ready']:
                vals['state'] = "ready"
        if vals.get('production_date_planned'):
            self.all_mrp_ids.write({
                'fal_floating_production_date': vals['production_date_planned']
            })
        if vals.get('production_date_fixed'):
            self.all_mrp_ids.write({
                'fal_fixed_production_date': vals['production_date_fixed']
            })
        return super(FalProductionOrderInherit, self).write(vals)

    is_ready = fields.Boolean(
        compute='_check_component_ready',
        string='Component Ready',
    )

    state = fields.Selection(selection_add=[('ready', 'Component ready')])

    @api.one
    def _check_component_ready(self):
        temp_is_component_ready = []
        for mrp in self.mrp_ids:
            temp_is_component_ready.append(mrp.fal_component_ready)
        if temp_is_component_ready and False not in temp_is_component_ready:
            self.is_ready = True

    @api.model
    def _prepare_mo_vals(self, bom):
        res = super(FalProductionOrderInherit, self)._prepare_mo_vals(bom)
        res['fal_floating_production_date'] = res['date_planned_start']
        return res
