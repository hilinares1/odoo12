from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class FalProductionOrder(models.Model):
    _name = 'fal.production.order'
    _description = 'Manage Production Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_location_src_id(self):
        location = False
        if self._get_default_picking_type():
            location = self.env['stock.picking.type'].browse(
                self._get_default_picking_type()).default_location_src_id
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']
            ).default_location_src_id
        if not location:
            location = self.env.ref(
                'stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self._get_default_picking_type():
            location = self.env['stock.picking.type'].browse(
                self._get_default_picking_type()).default_location_dest_id

        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(
                self.env.context['default_picking_type_id']
            ).default_location_dest_id

        if not location:
            location = self.env.ref(
                'stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            (
                'warehouse_id.company_id', 'in',
                [
                    self.env.context.get(
                        'company_id', self.env.user.company_id.id
                    ), False
                ]
            )
        ], limit=1).id

    # Field Definition
    name = fields.Char(string='Number', required=1, default='New',copy=False)
    combined_mo_names = fields.Char(
        string='Manufacturing Order', compute='get_mo_names', store=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('planned', 'Planned'),
            ('progress', 'In Progress'),
            ('done', 'Done'),
            ('cancel', 'Cancel'), ],
        string='Status', default='draft'
    )
    origin = fields.Char(string='Source', copy=False)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom', string='UoM',
        required=True
    )
    bom_id = fields.Many2one(
        'mrp.bom', string='BOM',
        required=True
    )
    qty_to_produce = fields.Float(
        string='Qty to Produce',
        required=True, default=1
    )
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda self: self.env[
            'res.company']._company_default_get('mrp.production')
    )
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type',
        default=_get_default_picking_type, required=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)

    # Date
    delivery_planned_date = fields.Datetime(
        string='Delivery Date', default=lambda *a: fields.Datetime.today())
    production_date_planned = fields.Datetime(
        string='Planned Date', default=lambda *a: fields.Datetime.today())
    production_date_fixed = fields.Datetime(
        string='Fixed Date')

    # MRP's
    mrp_ids = fields.One2many(
        'mrp.production', 'fal_prod_order_id',
        string='Manufacturing Orders')
    sub_mrp_ids = fields.Many2many(
        'mrp.production', string='Sub Manufacturing Orders', compute="_get_sub_mrp_ids")
    all_mrp_ids = fields.Many2many(
        'mrp.production', string='All Manufacturing Orders', compute="_get_all_mrp_ids")
    # Workorder
    workorder_ids = fields.One2many(
        'mrp.workorder', 'fal_prod_order_id', string='Work Orders')

    # Other Info
    wo_planned = fields.Boolean(string='Work Orders Planned')
    has_main_mo = fields.Boolean(
        string='Has Main MOs', compute='_get_has_main_mo')

    # Source
    location_src_id = fields.Many2one(
        'stock.location', 'Raw Materials Location',
        default=_get_default_location_src_id,
        readonly=True, required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest_id,
        readonly=True, required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will stock the finished products.")
    move_dest_ids = fields.Many2many(
        'stock.move',
        'fal_stock_move_move_rel', 'move_orig_id',
        'move_dest_id', 'Destination Moves',
        copy=False,
        help="Optional: next stock move when chaining them")

    # Procurement
    procurement_group_id = fields.Many2one(
        'procurement.group', 'Procurement Group',
        copy=False)
    propagate = fields.Boolean(
        'Propagate cancel and split',
        help='If checked, when the previous move of the move \
        (which was generated by a next procurement) \
        is cancelled or split, the move generated by this move will too')

    routing_id = fields.Many2one(
        'mrp.routing', 'Routing',
        readonly=True, compute='_compute_routing', store=True,
        help="The list of operations (list of work centers) to produce the finished product. The routing "
             "is mainly used to compute work center costs during operations and to plan future loads on "
             "work centers based on production planning.")

    @api.multi
    @api.depends('bom_id.routing_id', 'bom_id.routing_id.operation_ids')
    def _compute_routing(self):
        for production in self:
            if production.bom_id.routing_id.operation_ids:
                production.routing_id = production.bom_id.routing_id.id
            else:
                production.routing_id = False

    @api.depends('mrp_ids')
    def _get_sub_mrp_ids(self):
        for mpo in self:
            mpo.sub_mrp_ids = [(6, 0, self.env['mrp.production'].search([('id', 'not in', mpo.mrp_ids.ids), ('id', 'child_of', mpo.mrp_ids.ids)]).ids)]

    @api.depends('mrp_ids')
    def _get_all_mrp_ids(self):
        for mpo in self:
            mpo.all_mrp_ids = [(6, 0, self.env['mrp.production'].search([('id', 'child_of', mpo.mrp_ids.ids)]).ids)]

    @api.depends('all_mrp_ids')
    def get_mo_names(self):
        for mpo in self:
            names = mpo.all_mrp_ids.mapped('name')
            mpo.combined_mo_names = '  '.join(names)

    @api.depends('mrp_ids')
    def _get_has_main_mo(self):
        for item in self:
            if item.mrp_ids:
                item.has_main_mo = True
            else:
                item.has_main_mo = False

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if self.product_id:
            bom = self.env['mrp.bom']._bom_find(
                product=self.product_id,
                picking_type=self.picking_type_id,
                company_id=self.company_id.id
            )
            if bom.type == 'normal':
                self.bom_id = bom.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {
                'domain': {
                    'product_uom_id': [
                        (
                            'category_id', '=',
                            self.product_id.uom_id.category_id.id
                        )
                    ]
                }
            }

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].\
                next_by_code('fal.production.order') or 'New'
        return super(FalProductionOrder, self).create(vals)

    @api.multi
    def button_plan(self):
        for prod in self:
            prod.all_mrp_ids.button_plan()
            prod.write({'state': 'planned', 'wo_planned': True})

    @api.multi
    def button_unplan(self):
        for prod in self:
            prod.all_mrp_ids.button_unplan()

    @api.multi
    def button_confirm(self):
        for prod in self:
            prod.all_mrp_ids.button_confirm()
            prod.write({'state': 'confirm'})

    @api.multi
    def button_cancel(self):
        for prod in self:
            states = prod.all_mrp_ids.mapped('state')
            for state in states:
                if state != 'done':
                    # prod.all_mrp_ids.action_cancel()
                    # loop this because there is error on some case.
                    for mrp in prod.all_mrp_ids:
                        mrp.action_cancel()
                    prod.write({'state': 'cancel'})
                else:
                    raise UserError(_("You Cannot Cancel Production Order \
                        if You Have Done Manufacturing Order"))

    @api.multi
    def make_mo(self):
        """ Create manufacturing order from production order """
        res = []
        Production = self.env['mrp.production']
        for prod in self:
            ProductionSudo = Production.sudo().with_context(
                force_company=prod.company_id.id)
            bom = prod.bom_id
            if bom:
                # create the MO as SUPERUSER because the current
                # user may not have the rights to do it
                # (mto product launched by a sale for example)
                production = ProductionSudo.create(
                    prod._prepare_mo_vals(bom))
                group = production.procurement_group_id
                res.append(production)
            if group:
                childs = Production.search([
                    ('procurement_group_id', '=', group.id)])
                for po in childs:
                    po.fal_prod_order_id = prod.id
        return res

    @api.model
    def _get_date_planned(self):
        format_date_planned = fields.Datetime.from_string(
            self.production_date_planned)
        date_planned = format_date_planned - \
            relativedelta(days=self.product_id.produce_delay or 0.0)
        date_planned = date_planned - relativedelta(
            days=self.company_id.manufacturing_lead)
        return date_planned

    @api.model
    def _prepare_mo_vals(self, bom):
        date_planned_start = fields.Datetime.to_string(
            self._get_date_planned())
        propagate = False
        return {
            'origin': self.origin or self.name,
            'product_id': self.product_id.id,
            'product_qty': self.qty_to_produce,
            'product_uom_id': self.product_uom_id.id,
            'location_src_id': self.location_src_id.id,
            'location_dest_id': self.location_dest_id.id,
            'bom_id': bom.id,
            'date_planned_start': date_planned_start,
            'date_planned_finished': self.delivery_planned_date,
            'procurement_group_id': self.procurement_group_id.id,
            'propagate': propagate,
            'picking_type_id': self.picking_type_id.id or False,
            'company_id': self.company_id.id,
            'move_dest_ids': [(6, 0, self.move_dest_ids.ids)]
        }

    @api.multi
    def look_for_available_qty(self):
        # This method is used to check availability all raw material on all
        # Main MO and Sub MO
        for prod in self:
            mrp = prod.mrp_ids | prod.sub_mrp_ids
            mrp.action_assign()
        return True

    @api.multi
    def action_get_production_date_fixed_wizard(self):
        return {
            'name': 'Fill Production Date Fixed',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'fal.fill.production.date.fixed',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def production_fixed(self):
        for production in self:
            if production.production_date_planned:
                production.write({
                    'production_date_fixed': production.production_date_planned
                })
            else:
                production.write({
                    'production_date_fixed': fields.Date.today()
                })
