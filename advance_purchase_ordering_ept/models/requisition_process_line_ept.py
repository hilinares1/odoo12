from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class RequisitionProcessLine(models.Model):
    _name = "requisition.process.line.ept"
    _description = "Reorder Process Line"
    
    can_be_update = fields.Boolean(string='Allow to Update Adjusted Qty', default=True)
    qty_available_for_sale = fields.Integer(string='Lead Days Sales')
    requisition_qty = fields.Integer(string="Demanded Quantity")
    forecasted_stock = fields.Integer(string='Forecasted Stock')
    adjusted_requisition_qty = fields.Integer(string='Adjusted Demand',)
    expected_sale = fields.Integer(string="Expected Sale")
    sharing_percent = fields.Float(string="Sharing Percentage", digits=dp.get_precision('Payment Terms'))
    opening_stock = fields.Float(string="Opening Stock")
    state = fields.Selection([('draft', 'Draft'), ('generated', 'Calculated'), ('approved' , 'Approved')], string='Status', default='draft', index=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Requested Warehouse', index=True)
    requisition_process_id = fields.Many2one('requisition.process.ept', string='Reorder Process', index=True)
    product_id = fields.Many2one('product.product', string="Product", index=True)
    configuraiton_line_id = fields.Many2one('requisition.configuration.line.ept', string='Reorder Planning', index=True)
    requisition_summary_id = fields.Many2one('requisition.summary.line.ept', string='Reorder Summary')
    requisition_line_move_ids = fields.One2many('requisition.process.line.move.data', 'requisition_process_line_id', 'Incoming Moves')
    requisition_instock_qty = fields.Integer(string='Instock Qty')
