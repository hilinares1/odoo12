from odoo import models, fields, api


class FalHourlyCost(models.Model):
    _name = 'fal.hourly.cost'
    _description = "MRP Hourly Cost"

    name = fields.Char(string='Name')
    description = fields.Text(string='Description')
    default = fields.Boolean(string='Default')
    hourly_cost_type_ids = fields.One2many('fal.hourly.cost.type', 'hourly_cost_id', string='Cost Type')
    amount_total = fields.Monetary('Amount Total', compute='_compute_total', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('hourly_cost_type_ids', 'hourly_cost_type_ids.amount')
    def _compute_total(self):
        for item in self:
            amount = sum(
                (line.amount) for line in item.hourly_cost_type_ids)
            item.amount_total = amount


# I think the name of the class is not correct, it's reversed
class FalHourlyCostType(models.Model):
    _name = 'fal.hourly.cost.type'
    _description = "MRP Hourly Cost Line"

    name = fields.Char(string='Name')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    hourly_cost_id = fields.Many2one('fal.hourly.cost', string='Hourly Cost')
    hourly_cost_component_id = fields.Many2one(
        'fal.hourly.cost.component', string='Hourly Cost Component')


# I think the name of the class is not correct, it's reversed
class FalHourlyCostComponent(models.Model):
    _name = 'fal.hourly.cost.component'
    _description = "MRP Hourly Cost Type"

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class FalMrpCostPreview(models.Model):
    _name = 'fal.mrp.cost.preview'
    _description = "MRP Hourly Cost Preview"
    _order = "name asc"

    name = fields.Char(string='Name')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    cost_of_bom = fields.Monetary(string='Cost Of Bom', compute='_compute_total', currency_field='currency_id')
    hourly_cost = fields.Monetary(string='Cost of Routings', currency_field='currency_id')
    cost_of_scrap = fields.Monetary(
        string='Cost Of Scrap', compute='_compute_total', currency_field='currency_id')
    total = fields.Monetary(string='Total', compute='_compute_total', currency_field='currency_id')
    hourly_cost_component_id = fields.Many2one(
        'fal.hourly.cost.component', string='Hourly Cost Component')
    bom_id = fields.Many2one(
        'mrp.bom', string="Bom Id")

    @api.depends(
        'hourly_cost',
        'bom_id',
        'bom_id.fal_scrap_percentage',
        'bom_id.product_id',
        'bom_id.product_id.fal_bom_costs',
    )
    def _compute_total(self):
        for item in self:
            item.cost_of_scrap = (item.cost_of_bom + item.hourly_cost) \
                * item.bom_id.fal_scrap_percentage / 100.0
            product_id = item.bom_id.product_id or item.bom_id.product_tmpl_id or False
            if product_id:
                item.cost_of_bom = product_id.fal_bom_costs
            else:
                item.cost_of_bom = 0
            item.total = item.cost_of_bom + item.hourly_cost + item.cost_of_scrap
