from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class RequisitionConfigurationLine(models.Model):
    _name = 'requisition.configuration.line.ept'
    _description = "Reorder Planning"

    @api.model
    def _get_default_backup_stock_days(self):
        return self.env['ir.config_parameter'].sudo().get_param('inventory_coverage_report_ept.is_default_requisition_backup_stock_days')

    requisition_backup_stock_days = fields.Integer(string='Keep Stock of X Days', default=_get_default_backup_stock_days)
    requisition_estimated_delivery_time = fields.Integer(string='Lead Days')
    warehouse_id = fields.Many2one('stock.warehouse', string='Requested Warehouse', index=True)
    destination_warehouse_id = fields.Many2one('stock.warehouse', string='Delivery Warehouse', index=True)
    purchase_currency_id = fields.Many2one('res.currency', string="Purchase Currency")
    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order")
    requisition_process_id = fields.Many2one('requisition.process.ept', string='Reorder Process', index=True)
    po_schedule_date = fields.Date('Schedule Date', compute='compute_lead_coverage_date', store=True)
    coverage_start_date = fields.Date('Coverage Start Date', compute='compute_lead_coverage_date', store=True)
    coverage_end_date = fields.Date('Coverage End Date', compute='compute_lead_coverage_date', store=True)

    @api.constrains('warehouse_id', 'requisition_process_id')
    def _check_uniq_warehouse_id(self):
        for record in self :
            config_line_exists = self.search([('id', '!=', record.id), ('requisition_process_id', '=', record.requisition_process_id.id), ('warehouse_id', '=', record.warehouse_id.id)])
            if config_line_exists :
                raise ValidationError(_('Requested Warehouse must be unique per line'))

    @api.constrains('requisition_backup_stock_days', 'requisition_estimated_delivery_time')
    def check_security_days(self):
        for record in self:
            if record.requisition_backup_stock_days < 0:
                raise ValidationError(_("Stock Days can not be less than 0"))

            if record.requisition_estimated_delivery_time < 0:
                raise ValidationError(_("Estimated Delivery Time can not be less than 0"))
        return True

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        self.destination_warehouse_id = self.warehouse_id and self.warehouse_id.id or False

    @api.onchange('destination_warehouse_id')
    def onchange_destination_warehouse_id(self):
        for requisition_configuration_line_id in self.filtered(lambda
                                                                       x: x.destination_warehouse_id and x.requisition_process_id and x.requisition_process_id.partner_id):
            dest_warehouse = requisition_configuration_line_id.destination_warehouse_id
            partner = requisition_configuration_line_id.requisition_process_id.partner_id.with_context(
                force_company=dest_warehouse.company_id.id)
            currency = partner.property_purchase_currency_id or dest_warehouse and dest_warehouse.company_id and dest_warehouse.company_id.currency_id or False
            requisition_configuration_line_id.purchase_currency_id = currency
        return

    def get_warehouse_for_purchase_order(self):
        self.ensure_one()
        warehouse = self.destination_warehouse_id
        return warehouse

    @api.depends('requisition_estimated_delivery_time', 'requisition_backup_stock_days')
    def compute_lead_coverage_date(self):
        for config_line in self:
            product_suggestion_obj = self.env['requisition.product.suggestion.ept']
            po_schedule_date = False
            coverage_start_date = False
            coverage_end_date = False
            if config_line.requisition_process_id.requisition_date:
                po_schedule_date = product_suggestion_obj.get_next_date(config_line.requisition_process_id.requisition_date,
                                                                        days=config_line.requisition_estimated_delivery_time - 1 if config_line.requisition_estimated_delivery_time else 0)
                coverage_start_date = product_suggestion_obj.get_next_date(po_schedule_date, days=1)
                coverage_end_date = product_suggestion_obj.get_next_date(coverage_start_date,
                                                                         days=config_line.requisition_backup_stock_days - 1)
            config_line.po_schedule_date = po_schedule_date
            config_line.coverage_start_date = coverage_start_date
            config_line.coverage_end_date = coverage_end_date
