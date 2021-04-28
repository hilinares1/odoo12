# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @api.depends('partner_id')
    def _get_parent_company(self):
        for sale_order in self:
            sale_order.fal_parent_company = sale_order.partner_id.is_company and sale_order.partner_id.fal_parent_company or sale_order.partner_id.parent_id.fal_parent_company or False

    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
        related='partner_id.commercial_partner_id', store=True, readonly=True,
        help="The commercial entity that will be used on Journal Entries for this invoice")
    fal_parent_company = fields.Many2one(
        'res.partner',
        compute='_get_parent_company',
        string='Parent Company',
        help='The Parent Company for group',
        readonly=True,
        store=True
    )

# End of SaleOrder()
