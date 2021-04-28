from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    requisition_process_id = fields.Many2one('requisition.process.ept', string='Reorder Process',
                                             index=True, copy=False)
    warehouse_requisition_process_id = fields.Many2one('warehouse.requisition.process.ept',
                                                       string='Procurement Process')
    requisition_configuration_line_ids = fields.One2many('requisition.configuration.line.ept',
                                                         'purchase_order_id',
                                                         string="Reorder Plannings")



