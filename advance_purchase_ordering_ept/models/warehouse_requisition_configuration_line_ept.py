from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class WarehouseRequisitionProcessLine(models.Model):
    _name = 'warehouse.requisition.configuration.line.ept'
    _description = "Procurement Process Warehouse Planning"

    requisition_estimated_delivery_time = fields.Integer(string='Estimated Delivery Time')
    requisition_backup_stock_days = fields.Integer(string='Keep Stock of X Days',
                                                   default=lambda self: self.env[
                                                                            'ir.config_parameter'].sudo().get_param(
                                                       'inventory_coverage_report_ept.is_default_requisition_backup_stock_days') or 1)
    warehouse_id = fields.Many2one('stock.warehouse', string='Requested Warehouse', index=True)
    warehouse_requisition_process_id = fields.Many2one('warehouse.requisition.process.ept',
                                                       string='Procurement Process', index=True,
                                                       copy=False)
    destination_warehouse_id = fields.Many2one('stock.warehouse', string='Delivery warehouse',
                                               index=True)
    intercompany_transfer_id = fields.Many2one('inter.company.transfer.ept',
                                               string="Inter-Company Transfer")
    schedule_date = fields.Date('Schedule Date', compute='compute_lead_coverage_date',
                                   store=True)
    coverage_start_date = fields.Date('Coverage Start Date', compute='compute_lead_coverage_date',
                                      store=True)
    coverage_end_date = fields.Date('Coverage End Date', compute='compute_lead_coverage_date',
                                    store=True)

    @api.constrains('warehouse_id', 'warehouse_requisition_process_id')
    def _check_uniq_warehouse_id(self):
        for line in self:
            config_line_exists = self.search([('id', '!=', line.id), (
            'warehouse_requisition_process_id', '=', line.warehouse_requisition_process_id.id),
                                              ('warehouse_id', '=', line.warehouse_id.id)])
            if config_line_exists:
                raise ValidationError(_('Requested Warehouse must be unique per line'))

    @api.constrains('destination_warehouse_id')
    def _check_dest_warehouse(self):
        for line in self:
            if line.warehouse_requisition_process_id.source_warehouse_id == line.warehouse_id:
                if line.warehouse_id != line.destination_warehouse_id:
                    raise ValidationError(_(
                        'Delivery Warehouse Must be Same as Source Warehouse If Warehouse in Configuration Line and Source Warehouse Both are Same.'))

    @api.constrains('requisition_backup_stock_days', 'requisition_estimated_delivery_time')
    def check_security_days(self):
        for line in self:
            if line.requisition_backup_stock_days < 0:
                raise ValidationError(_("Stock Days can not be less than 0"))

            if line.requisition_estimated_delivery_time < 0:
                raise ValidationError(_("Estimated Delivery Time can not be less than 0"))
        return True

    def is_create_intercompany_transfer(self):
        return True

    def get_warehouse_for_ict(self):
        self.ensure_one()
        warehouse = self.destination_warehouse_id
        return warehouse

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.destination_warehouse_id = self.warehouse_id and self.warehouse_id.id or False

    @api.depends('requisition_estimated_delivery_time', 'requisition_backup_stock_days')
    def compute_lead_coverage_date(self):
        for config_line in self:
            product_suggestion_obj = self.env['requisition.product.suggestion.ept']
            schedule_date = False
            coverage_start_date = False
            coverage_end_date = False
            if config_line.warehouse_requisition_process_id.requisition_date:
                schedule_date = product_suggestion_obj.get_next_date(
                    config_line.warehouse_requisition_process_id.requisition_date,
                    days=config_line.requisition_estimated_delivery_time - 1 if config_line.requisition_estimated_delivery_time else 0)
                coverage_start_date = product_suggestion_obj.get_next_date(schedule_date, days=1)
                coverage_end_date = product_suggestion_obj.get_next_date(coverage_start_date,
                                                                         days=config_line.requisition_backup_stock_days - 1)
            config_line.schedule_date = schedule_date
            config_line.coverage_start_date = coverage_start_date
            config_line.coverage_end_date = coverage_end_date
