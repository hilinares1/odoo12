from odoo import models, fields, api


class RequisitionProcessLineMoveData(models.Model):
    _name = "requisition.process.line.move.data"
    _description = "requisition process line move data"

    move_id = fields.Many2one('stock.move', 'Stock Move')
    schedule_date = fields.Date('Schedule Date')
    quantity = fields.Float('Quantity')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    picking_id = fields.Many2one('stock.picking', 'Picking')
    product_id = fields.Many2one('product.product', 'Product')
    requisition_process_line_id = fields.Many2one('requisition.process.line.ept',
                                                  'Requisition Process Line')
    warehouse_requisition_process_line_id = fields.Many2one(
        'warehouse.requisition.process.line.ept',
        string='Warehouse Requisition Process Line')
