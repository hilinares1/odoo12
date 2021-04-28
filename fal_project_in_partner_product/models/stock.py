from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fal_project_numbers = fields.Char(compute='_get_projects', string='Project Numbers', help='The projects.', store=True)

    @api.depends('move_lines', 'move_lines.fal_project_id')
    def _get_projects(self):
        for picking in self:
            temp = []
            for line in picking.move_lines:
                if line.fal_project_id and line.fal_project_id.code not in temp:
                    temp.append(line.fal_project_id.code or line.fal_project_id.name)
                    if temp:
                        picking.fal_project_numbers = "; ".join(temp)
                    else:
                        picking.fal_project_numbers = ""


class StockMove(models.Model):
    _inherit = "stock.move"

    fal_project_id = fields.Many2one('account.analytic.account', string='Analytic Account')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for data in res:
            data['fal_project_id'] = self.account_analytic_id.id
        return res


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        res = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        sale_line_id = self.env['sale.order.line'].browse(values['sale_line_id'])
        res['fal_project_id'] = sale_line_id.order_id.analytic_account_id.id
        return res
