from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class QualityPoint(models.Model):
    _inherit = 'quality.point'

    measure_frequency_unit = fields.Selection(
        selection_add=[('hours', 'Hour(s)')])
    fal_test_type_ids = fields.Many2many(
        'fal.test.type', string='Test Types')
    # Template
    fal_quality_point_template = fields.Boolean(
        string='Quality Point Template', default=False)
    fal_product_category = fields.Many2one(
        'product.category', string='Product Category')
    # There is possibility that because of template, we don't have the product id
    product_tmpl_id = fields.Many2one(required=False)


class FalTestType(models.Model):
    _name = 'fal.test.type'
    _description = 'Test Type'

    sequence = fields.Integer(help='Used to order test type')
    name = fields.Char(string='Test Type Name')
    picking_type_id = fields.Many2one('stock.picking.type', "Operation Type", required=True)
    test_type = fields.Selection([
        ('view', 'View'),
        ('normal', 'Normal')
    ], 'Type of Test', required=True, default='normal')
    parent_id = fields.Many2one(
        'fal.test.type', 'Parent Test Type',
        domain="[('test_type', '=', 'view')]")


class FalQualityCheck(models.Model):
    _name = 'fal.quality.check'
    _description = 'Quality Check'

    name = fields.Char(string='Test Type')
    quality_check_id = fields.Many2one('quality.check')
    # no use this for a moment
    checklist = fields.Boolean(string='OK', default=False)
    check_no_ok = fields.Boolean(string='No OK', default=False)
    check_no_applicable = fields.Boolean(string='No Applicable', default=False)
    # =========================
    notes = fields.Text(string='Notes')
    fal_test_type_id = fields.Many2one('fal.test.type', string="Test Type id")
    fal_parent_test_type_id = fields.Many2one('fal.test.type', string="Parent Test Type ID")
    # use for quantity test
    total_check_ok = fields.Integer(string="Total OK", compute='_compute_total_check_ok', store=True)
    total_check_no_ok = fields.Integer(string="Total Not OK", default=0)
    total_check_no_applicable = fields.Integer(string="Total Not Applicable", default=0)
    fal_total_qty_to_check = fields.Integer(string="Total Qty to Check")

    # no use this for a moment
    @api.onchange('checklist')
    def set_checklist_ok(self):
        if self.checklist:
            self.check_no_ok = False
            self.check_no_available = False

    @api.onchange('check_no_ok')
    def set_check_no_ok(self):
        if self.check_no_ok:
            self.checklist = False
            self.check_no_available = False

    @api.onchange('check_no_applicable')
    def set_check_no_available(self):
        if self.check_no_applicable:
            self.checklist = False
            self.check_no_ok = False
    # =========================

    @api.onchange('total_check_no_ok', 'total_check_no_applicable')
    def set_value_total_check(self):
        if self.total_check_no_ok + self.total_check_no_applicable > self.fal_total_qty_to_check:
            raise ValidationError(_('Total Not OK + Total Not Applicable cannot exceeds the value of Total Qty to check.'))
        elif self.total_check_no_ok < 0:
            raise ValidationError(_('Total Not OK should be positive.'))
        elif self.total_check_no_applicable < 0:
            raise ValidationError(_('Total Not Applicable should be positive.'))

    @api.one
    @api.depends('total_check_no_ok', 'total_check_no_applicable')
    def _compute_total_check_ok(self):
        self.total_check_ok = self.fal_total_qty_to_check - self.total_check_no_ok - self.total_check_no_applicable


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    fal_quality_check_ids = fields.Many2many('fal.quality.check', string="Quality Check")
    fal_description = fields.Char(
        string='Sale Description', copy=False, readonly=True, index=True)


class QualityCheck(models.Model):
    _inherit = 'quality.check'

    fal_quality_check_ids = fields.One2many(
        'fal.quality.check', 'quality_check_id')
    fal_total_qty_to_check = fields.Integer(string='Total Qty to Check', default=0)
    fal_total_qty_pass = fields.Integer(string='Total Qty of Tests Passed', default=0, compute='_compute_fal_total_qty', store=True)
    fal_total_qty_failed = fields.Integer(string='Total Qty of Tests Failed', default=0, compute='_compute_fal_total_qty', store=True)
    fal_description = fields.Char(string='Order Reference', copy=False, readonly=True, index=True)

    @api.multi
    @api.depends(
        'fal_quality_check_ids',
        'fal_quality_check_ids.total_check_ok',
        'fal_quality_check_ids.total_check_no_ok')
    def _compute_fal_total_qty(self):
        for value in self:
            total_qty_to_check = 0
            total_checklist_ok = 0
            total_checklist_no_ok = 0

            for checked_activity in value.fal_quality_check_ids:
                total_qty_to_check += checked_activity.fal_total_qty_to_check
                total_checklist_ok += checked_activity.total_check_ok
                total_checklist_no_ok += checked_activity.total_check_no_ok

            value.fal_total_qty_pass = total_checklist_ok
            value.fal_total_qty_failed = total_checklist_no_ok

    @api.multi
    def do_pass(self):
        for item in self:
            for check in item.fal_quality_check_ids:
                # use for quantity test
                total_check = check.total_check_ok + check.total_check_no_applicable
                if check.fal_total_qty_to_check > total_check:
                    raise UserError(_(
                        'Cannot pass the product, \
                        because there is a not ok activity'))
                # use for checklist
                # remove if not use checlist test.
                # product_check = len(check.search([
                #     ('quality_check_id', '=', item.id)]))
                # checklist_check = len(check.search([
                #     ('checklist', '=', True),
                #     ('quality_check_id', '=', item.id)]))
                # if product_check > checklist_check:
                #     raise UserError(_(
                #         'Cannot pass the product, \
                #         because there is an uncheck test type'))
        return super(QualityCheck, self).do_pass()

    def _values_alert(self):
        return {
            'check_id': self.id,
            'product_id': self.product_id.id,
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            'lot_id': self.lot_id.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'company_id': self.company_id.id,
            'fal_description': self.fal_description,
        }

    @api.multi
    def do_fail(self):
        check_no_ok = 0

        for item in self:
            for check in item.fal_quality_check_ids:
                check_no_ok += check.total_check_no_ok
            if check_no_ok == 0:
                raise UserError(_(
                    'Cannot fail the product because there should be not ok activity.'))

            # Automatically generate Alert
            alert_id = request.env['quality.alert'].create(self._values_alert())
            alert_id.fal_quality_check_ids = [(6, 0, item.fal_quality_check_ids.ids)]

        return super(QualityCheck, self).do_fail()
