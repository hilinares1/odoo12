from odoo import fields, models, api


class WarehouseRequisitionProcessLine(models.Model):
    _name = 'warehouse.requisition.process.line.ept'
    _description = "Procurement Process Calculation Lines"
       
    can_be_update = fields.Boolean(string='Allow to Update Adjusted Qty', default=True)
    qty_available_for_sale = fields.Integer(string='Lead Days Sales')
    requisition_qty = fields.Integer(string='Demanded Quantity')
    forecasted_stock = fields.Integer(string='Forecasted Stock')
    adjusted_requisition_qty = fields.Integer(string='Adjusted Demand')
    expected_sale = fields.Integer(string='Expected Sale')
    state = fields.Selection([('draft', 'Draft'), ('generated', 'Calculated'), ('approved' , 'Approved'), ('done', 'Done') ], string='Status', default='draft', required=True, index=True)
    sharing_percent = fields.Float(string='Sharing Percentage')
    opening_stock = fields.Float(string="Opening Stock")
    warehouse_id = fields.Many2one('stock.warehouse', string='Requested Warehouse', index=True)
    warehouse_requisition_process_id = fields.Many2one('warehouse.requisition.process.ept', string='Procurement Process', index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Product', index=True)
    warehouse_configuraiton_line_id = fields.Many2one('warehouse.requisition.configuration.line.ept', string='Procurement Planning', index=True, copy=False)
    warehouse_requisition_summary_id = fields.Many2one('warehouse.requisition.summary.line.ept', string='Procurement Summary', copy=False)
    warehouse_requisition_line_move_ids = fields.One2many('requisition.process.line.move.data', 'warehouse_requisition_process_line_id', 'Incoming Moves')
    warehouse_requisition_instock_qty = fields.Integer(string='Instock Qty')
