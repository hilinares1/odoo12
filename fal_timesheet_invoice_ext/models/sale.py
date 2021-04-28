from odoo import fields, models, api
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    timesheet_ids = fields.Many2many(compute='_compute_timesheet_ids')
    timesheet_count = fields.Float(compute='_compute_timesheet_ids')

    @api.multi
    @api.depends('analytic_account_id.line_ids')
    def _compute_timesheet_ids(self):
        for order in self:
            order.timesheet_ids = self.env['account.analytic.line'].\
                search([
                    ('is_timesheet', '=', True),
                    ('account_id', '=', order.analytic_account_id.id),
                    ('task_id.sale_line_id', 'in', order.order_line.ids)
                ]) if order.analytic_account_id else []
            order.timesheet_count = round(sum(
                [line.unit_amount if not line.to_invoice else line.unit_amount_coef for line in order.timesheet_ids]), 2)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_delivered_quantity_by_analytic(self, additional_domain):
        result = super(SaleOrderLine, self)._get_delivered_quantity_by_analytic(additional_domain)
        # avoid recomputation if no SO lines concerned
        if not self:
            return result

        # group anaytic lines by product uom and so line
        domain = expression.AND([[('so_line', 'in', self.ids)], additional_domain])
        data = self.env['account.analytic.line'].read_group(
            domain,
            ['so_line', 'unit_amount', 'product_uom_id'], ['product_uom_id', 'so_line'], lazy=False
        )

        # convert uom and sum all unit_amount of analytic lines to get the delivered qty of SO lines
        # browse so lines and product uoms here to make them share the same prefetch
        lines_map = {line.id: line for line in self}
        product_uom_ids = [item['product_uom_id'][0] for item in data if item['product_uom_id']]
        product_uom_map = {uom.id: uom for uom in self.env['uom.uom'].browse(product_uom_ids)}
        for item in data:
            if not item['product_uom_id']:
                continue
            so_line_id = item['so_line'][0]
            so_line = lines_map[so_line_id]
            result.setdefault(so_line_id, 0.0)
            uom = product_uom_map.get(item['product_uom_id'][0])
            if so_line.product_uom.category_id == uom.category_id:
                qty = uom._compute_quantity(item['unit_amount'], so_line.product_uom)
            else:
                qty = item['unit_amount']
            result[so_line_id] += qty
            timesheet = self.env['account.analytic.line'].\
                search([
                    ('is_timesheet', '=', True),
                    ('account_id', '=', so_line.order_id.analytic_account_id.id),
                    ('task_id.sale_line_id', '=', so_line.id)
                ])
            new_qty = round(sum(
                [line.unit_amount if not line.to_invoice else line.unit_amount_coef for line in timesheet]), 2)
            result[so_line_id] = new_qty
        return result

# merge from falinwa_field_ext
