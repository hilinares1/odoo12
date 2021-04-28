from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fal_prod_order_id = fields.Many2one('fal.production.order', string='Direct Production Order')
    fal_parent_prod_order_id = fields.Many2one('fal.production.order', string='Parent Production Order', related="parent_id.fal_prod_order_id", store=True)
    fal_parent_or_prod_order_id = fields.Many2one('fal.production.order', string='Production Order', compute="_get_parent_prod_order_id", store=True)
    parent_id = fields.Many2one('mrp.production', 'Parent MO', copy=False)
    child_ids = fields.One2many('mrp.production', 'parent_id', string='Sub Manufacturing Order', copy=False)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('planned', 'Planned'),
            ('progress', 'In Progress'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], default='draft'
    )
    product_id = fields.Many2one(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    product_qty = fields.Float(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    product_uom_id = fields.Many2one(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    location_src_id = fields.Many2one(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    date_planned_start = fields.Datetime(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    date_planned_finished = fields.Datetime(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    bom_id = fields.Many2one(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})
    priority = fields.Selection(states={'confirmed': [('readonly', False)], 'draft': [('readonly', False)]})

    @api.multi
    @api.depends('fal_prod_order_id', 'fal_parent_prod_order_id')
    def _get_parent_prod_order_id(self):
        for mpo in self:
            if mpo.fal_prod_order_id:
                mpo.fal_parent_or_prod_order_id = mpo.fal_prod_order_id.id
            elif mpo.fal_parent_prod_order_id:
                mpo.fal_parent_or_prod_order_id = mpo.fal_parent_prod_order_id.id

    @api.multi
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        # Try to mark done the production order, if all the mrp.production is finished
        for mrp in self:
            mrps = mrp.fal_prod_order_id and \
                mrp.fal_prod_order_id.all_mrp_ids and \
                mrp.fal_prod_order_id.all_mrp_ids.filtered(
                    lambda r: not r.parent_id)
            if all(mrp.state == 'done' for mrp in mrps):
                mrp.fal_prod_order_id.write({'state': 'done'})
        return res

    # Because we have draft state, we will make a stage to move it onto confirmed state
    @api.multi
    def button_confirm(self):
        for mrp in self:
            mrp.write({'state': 'confirmed'})
            # Try to mark confirmed the production order, if all the mrp.production is confirmed
            mrps = mrp.fal_prod_order_id and \
                mrp.fal_prod_order_id.all_mrp_ids and \
                mrp.fal_prod_order_id.all_mrp_ids.filtered(
                    lambda r: not r.parent_id)
            if all(_mrp.state == 'confirmed' for _mrp in mrps):
                mrp.fal_prod_order_id.write({'state': 'confirm'})

    @api.multi
    def button_plan(self):
        res = super(MrpProduction, self).button_plan()
        # Try to mark planned the production order, if all the mrp.production is planned
        for mrp in self:
            mrps = mrp.fal_prod_order_id and \
                mrp.fal_prod_order_id.all_mrp_ids and \
                mrp.fal_prod_order_id.all_mrp_ids.filtered(
                    lambda r: not r.parent_id)
            if all(mrp.state == 'planned' for mrp in mrps):
                mrp.fal_prod_order_id.write({'state': 'planned'})
        return res

    # Tree View action
    @api.multi
    def action_open_form_view(self):
        context = dict(self.env.context or {})
        self.ensure_one()
        return{
            'name': _('Manufacturing Order'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'view_id': self.env.ref('mrp.mrp_production_form_view').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'context': context,
            'target': 'current'
        }


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    fal_prod_order_id = fields.Many2one(
        'fal.production.order', related='production_id.fal_prod_order_id',
        string='Production Order', store=True, copy=False
    )

    @api.multi
    @api.depends('name', 'fal_prod_order_id', 'production_id')
    def name_get(self):
        result = []
        for wo in self:
            name = wo.name
            if wo.production_id:
                name = wo.production_id.name + '/' + name
            if wo.fal_prod_order_id:
                name = wo.fal_prod_order_id.name + '/' + name
            result.append((wo.id, name))
        return result

    @api.multi
    def button_start(self):
        res = super(MrpWorkOrder, self).button_start()
        # Try to mark progress the production order, if all the mrp.production is progress
        mrps = self.fal_prod_order_id and self.fal_prod_order_id.mrp_ids and \
            self.fal_prod_order_id.mrp_ids.filtered(lambda r: not r.parent_id)
        if all(mrp.state == 'progress' for mrp in mrps):
            self.fal_prod_order_id.write({'state': 'progress'})
        return res
