from odoo import fields, models, api, _


class InterCompanyTransfer(models.Model):
    _inherit = 'inter.company.transfer.ept'
    _description = 'Inter Company Transfer'

    warehouse_requisition_process_id = fields.Many2one('warehouse.requisition.process.ept',
                                                       string='Procurement Process')
    warehouse_configuration_line_ids = fields.One2many(
        'warehouse.requisition.configuration.line.ept', 'intercompany_transfer_id',
        string="Procurement Process Planning")

    def auto_create_saleorder(self):
        sale_orders = super(InterCompanyTransfer, self).auto_create_saleorder()
        for so in sale_orders:
            so.warehouse_requisition_process_id = so.intercompany_transfer_id.warehouse_requisition_process_id and so.intercompany_transfer_id.warehouse_requisition_process_id.id or False
        return sale_orders

    def auto_create_purchaseorder(self):
        purchase_orders = super(InterCompanyTransfer, self).auto_create_purchaseorder()
        for po in purchase_orders:
            if po.intercompany_transfer_id.warehouse_requisition_process_id:
                po.warehouse_requisition_process_id = po.intercompany_transfer_id.warehouse_requisition_process_id and po.intercompany_transfer_id.warehouse_requisition_process_id.id or False
        return purchase_orders
